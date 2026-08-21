from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "trade-ai-service"
    environment: str = "development"
    log_level: str = "INFO"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "trade-ai-service"
    market_snapshot_topic: str = "market.snapshot"
    signal_generated_topic: str = "signal.generated"
    ai_decision_topic: str = "ai.decision"
    kafka_auto_offset_reset: str = "latest"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_temperature: float = Field(default=0.1, ge=0, le=2)
    ai_version: str = "1.0.0"
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_max_retries: int = Field(default=2, ge=0, le=10)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
