import asyncio
import logging

from app.config.settings import Settings
from app.kafka.consumer import KafkaConsumer
from app.models.market_snapshot import MarketSnapshot
from app.models.signal_generated import SignalGenerated
from app.services.decision_service import DecisionService

logger = logging.getLogger(__name__)


class ContextService:
    def __init__(self, settings: Settings, decision_service: DecisionService):
        self._settings = settings
        self._decision_service = decision_service
        self._snapshots: dict[tuple[str, str], MarketSnapshot] = {}
        self._signals: dict[tuple[str, str], SignalGenerated] = {}
        self._consumer = KafkaConsumer(
            settings.kafka_bootstrap_servers,
            settings.kafka_group_id,
            [settings.market_snapshot_topic, settings.signal_generated_topic],
            settings.kafka_auto_offset_reset,
        )

    async def run(self) -> None:
        await self._consumer.run(self.handle_message)

    async def handle_message(self, topic: str, payload: dict) -> None:
        if topic == self._settings.market_snapshot_topic:
            event = MarketSnapshot.model_validate(payload)
            key = (event.symbol, event.timeframe)
            self._snapshots[key] = event
        elif topic == self._settings.signal_generated_topic:
            event = SignalGenerated.model_validate(payload)
            key = (event.symbol, event.timeframe)
            self._signals[key] = event
        else:
            return

        key = (event.symbol, event.timeframe)
        signal = self._signals.get(key)
        snapshot = self._snapshots.get(key)
        if signal and snapshot:
            await self._decision_service.evaluate(signal, snapshot)
            self._signals.pop(key, None)
