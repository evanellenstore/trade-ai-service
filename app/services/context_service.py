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
        # Keep the Kafka listener running and route every received message to the context handler.
        print("Context service started; waiting for Kafka events", flush=True)
        await self._consumer.run(self.handle_message)

    async def handle_message(self, topic: str, payload: dict) -> None:
        # Deserialize each supported topic into its typed event and index it by symbol and timeframe.
        if topic == self._settings.market_snapshot_topic:
            event = MarketSnapshot.model_validate(payload)
            key = (event.symbol, event.timeframe)
            self._snapshots[key] = event
        elif topic == self._settings.signal_generated_topic:
            event = SignalGenerated.model_validate(payload)
            key = (event.symbol, event.timeframe)
            self._signals[key] = event
        else:
            print(f"Unsupported Kafka topic ignored: topic={topic}", flush=True)
            return

        # Keep immediate console visibility for local debugging of the Kafka-to-decision flow.
        print(f"Context event stored: topic={topic}, symbol={event.symbol}, timeframe={event.timeframe}", flush=True)

        # A decision requires both a market snapshot and a generated signal for the same context.
        key = (event.symbol, event.timeframe)
        signal = self._signals.get(key)
        snapshot = self._snapshots.get(key)
        if signal and snapshot:
            # Evaluate the complete pair, then remove the signal to prevent duplicate processing.
            print(f"Complete trading context found: symbol={event.symbol}, timeframe={event.timeframe}", flush=True)
            await self._decision_service.evaluate(signal, snapshot)
            self._signals.pop(key, None)
            print(f"AI decision evaluation completed: symbol={event.symbol}, timeframe={event.timeframe}", flush=True)
        else:
            print(f"Waiting for matching event: symbol={event.symbol}, timeframe={event.timeframe}", flush=True)
