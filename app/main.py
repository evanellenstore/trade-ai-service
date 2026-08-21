import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.responses import Response

from app.agents.decision_agent import DecisionAgent
from app.api.health import create_health_router
from app.config.settings import get_settings
from app.kafka.producer import KafkaProducer
from app.llm.ollama_client import OllamaClient
from app.services.context_service import ContextService
from app.services.decision_service import DecisionService

DECISIONS = Counter("trade_ai_decisions_total", "AI decisions published", ["decision"])


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    producer = KafkaProducer(settings.kafka_bootstrap_servers)
    await producer.start()
    decision_service = DecisionService(settings, producer, DecisionAgent(OllamaClient(settings)))
    context_service = ContextService(settings, decision_service)
    consumer_task = asyncio.create_task(context_service.run(), name="kafka-consumer")
    app.state.context_service = context_service
    try:
        yield
    finally:
        consumer_task.cancel()
        await asyncio.gather(consumer_task, return_exceptions=True)
        await producer.stop()


app = FastAPI(title="Trade AI Service", version=get_settings().ai_version, lifespan=lifespan)
app.include_router(create_health_router(get_settings().app_name))


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
