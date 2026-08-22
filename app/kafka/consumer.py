import json
import logging
from collections.abc import Awaitable, Callable

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)
MessageHandler = Callable[[str, dict], Awaitable[None]]


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list[str], auto_offset_reset: str):
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )

    async def run(self, handler: MessageHandler) -> None:
        await self._consumer.start()
        print("Kafka consumer started and listening for messages", flush=True)
        try:
            async for message in self._consumer:
                try:
                    print(f"Kafka message received: topic={message.topic}, value={message.value}", flush=True)
                    await handler(message.topic, message.value)
                    print(f"Kafka message processed: topic={message.topic}", flush=True)
                except Exception:
                    print(f"Kafka message processing failed: topic={message.topic}", flush=True)
                    logger.exception("kafka_message_processing_failed", extra={"topic": message.topic})
        finally:
            await self._consumer.stop()
            print("Kafka consumer stopped", flush=True)
