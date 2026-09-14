from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class SignalGenerated(BaseModel):
    model_config = ConfigDict(extra="ignore")

    signal_id: str = Field(alias="signalId")
    symbol: str
    symbol_token: str = Field(alias="symbolToken")
    timeframe: str
    strategy_name: str = Field(alias="strategyName")
    signal: str
    confidence: float = Field(ge=0, le=100)
    price: float = Field(gt=0)
    reason: str = ""
    timestamp: datetime | None = None
