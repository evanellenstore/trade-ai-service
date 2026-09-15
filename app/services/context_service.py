import asyncio
import logging
from datetime import datetime, timedelta

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
        self._snapshots: dict[tuple[str, str, datetime | None], MarketSnapshot] = {}
        self._signals: dict[tuple[str, str, datetime | None], SignalGenerated] = {}
        self._consumer = KafkaConsumer(
            settings.kafka_bootstrap_servers,
            settings.kafka_group_id,
            [settings.market_snapshot_topic, settings.signal_generated_topic],
            settings.kafka_auto_offset_reset,
        )

    @staticmethod
    def _event_time(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=None)

    @staticmethod
    def _time_delta_seconds(left: datetime | None, right: datetime | None) -> float | None:
        if left is None or right is None:
            return None
        return abs((left - right).total_seconds())

    def _find_matching_event(self, bucket: dict[tuple[str, str, datetime | None], object], symbol: str,
                             timeframe: str, event_time: datetime | None) -> object | None:
        if event_time is not None:
            exact_key = (symbol, timeframe, event_time)
            if exact_key in bucket:
                return bucket[exact_key]

            for key, value in bucket.items():
                if key[0] != symbol or key[1] != timeframe or key[2] is None:
                    continue
                delta = self._time_delta_seconds(event_time, key[2])
                if delta is not None and delta <= 60:
                    return value

        legacy_key = (symbol, timeframe, None)
        return bucket.get(legacy_key)

    async def run(self) -> None:
        # Keep the Kafka listener running and route every received message to the context handler.
        print(" 1. ============ ========== Context service started; waiting for Kafka events", flush=True)
        await self._consumer.run(self.handle_message)

    async def handle_message(self, topic: str, payload: dict) -> None:
        # Deserialize each supported topic into its typed event and index it by symbol and timeframe.
        if topic == self._settings.market_snapshot_topic:
            event = MarketSnapshot.model_validate(payload)
            key = (event.symbol, event.timeframe, self._event_time(event.snapshot_time))
            self._snapshots[key] = event
        elif topic == self._settings.signal_generated_topic:
            event = SignalGenerated.model_validate(payload)
            key = (event.symbol, event.timeframe, self._event_time(event.timestamp))
            self._signals[key] = event
        else:
            print(f" 2. ============ ========== Unsupported Kafka topic ignored: topic={topic}", flush=True)
            return

        print(f" 3. ============ ========== Context event stored: topic={topic}, symbol={event.symbol}, timeframe={event.timeframe}", flush=True)

        event_time = self._event_time(event.snapshot_time) if topic == self._settings.market_snapshot_topic else self._event_time(event.timestamp)
        print(f" 4. ============ ========== Context key: {(event.symbol, event.timeframe, event_time)}", flush=True)
        signal = self._find_matching_event(self._signals, event.symbol, event.timeframe, event_time)
        print(f" 5. ============ ========== Retrieved signal: {signal is not None}", flush=True)
        snapshot = self._find_matching_event(self._snapshots, event.symbol, event.timeframe, event_time)
        print(f" 6. ============ ========== Retrieved snapshot: {snapshot is not None}", flush=True)
        if signal and snapshot:
            print(f" 7. ============ ========== Complete trading context found: symbol={event.symbol}, timeframe={event.timeframe}", flush=True)
            await self._decision_service.evaluate(signal, snapshot)
            signal_key = (signal.symbol, signal.timeframe, self._event_time(signal.timestamp))
            self._signals.pop(signal_key, None)
            print(f" ============ ========== AI decision evaluation completed: symbol={event.symbol}, timeframe={event.timeframe}", flush=True)
        else:
            print(f"============ ========== Waiting for matching event: symbol={event.symbol}, timeframe={event.timeframe}", flush=True)
