from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AIDecision(BaseModel):
    model_config = ConfigDict(extra="ignore")

    decision: str
    confidence: int = Field(ge=0, le=100)
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"BUY", "SELL", "HOLD"}:
            raise ValueError("decision must be BUY, SELL, or HOLD")
        return normalized


class AIDecisionEvent(AIDecision):
    signal_id: str = Field(alias="signalId")
    symbol: str
    strategy: str
    ai_version: str = Field(alias="aiVersion")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
