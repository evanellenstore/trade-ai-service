from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.market_snapshot import Candle, _parse_datetime_value


class SignalGenerated(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    signal_id: str | None = Field(default=None, alias="signalId")
    symbol: str
    symbol_token: str | None = Field(default=None, alias="symbolToken")
    timeframe: str
    strategy_name: str | None = Field(default=None, alias="strategyName")
    signal: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=100)
    price: float | None = Field(default=None, gt=0)
    reason: str = ""
    timestamp: datetime | None = None
    candles: list[Candle] = Field(default_factory=list)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        return _parse_datetime_value(value)
