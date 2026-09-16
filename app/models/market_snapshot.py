from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _parse_datetime_value(value):
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).replace(tzinfo=None)
    if isinstance(value, list):
        if not value:
            return None
        return datetime(*value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).replace(tzinfo=None)
    return value


class Candle(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    symbol: str
    symbol_token: str | None = Field(default=None, alias="symbolToken")
    exchange: str = ""
    subscription_id: str | None = Field(default=None, alias="subscriptionId")
    subscription_name: str | None = Field(default=None, alias="subscriptionName")
    timeframe: str | None = None
    candle_time: datetime | None = Field(default=None, alias="candleTime")
    end_time: datetime | None = Field(default=None, alias="endTime")
    start_time: datetime | None = Field(default=None, alias="startTime")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    ltp: float | None = 0.0

    @field_validator("candle_time", "end_time", "start_time", "created_at", mode="before")
    @classmethod
    def parse_datetime_fields(cls, value):
        return _parse_datetime_value(value)


class MarketSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    symbol: str
    symbol_token: str | None = Field(default=None, alias="symbolToken")
    exchange: str = ""
    subscription_id: str | None = Field(default=None, alias="subscriptionId")
    subscription_name: str | None = Field(default=None, alias="subscriptionName")
    timeframe: str
    price: float = Field(default=0.0, gt=0)
    trend: str = "UNKNOWN"
    trend_strength: str | None = Field(default=None, alias="trendStrength")
    market_regime: str | None = Field(default=None, alias="marketRegime")
    volume_spike: bool = Field(alias="volumeSpike", default=False)
    rsi14: Optional[float] = None
    adx: Optional[float] = None
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema100: Optional[float] = None
    ema200: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = Field(alias="macdSignal", default=None)
    macd_histogram: Optional[float] = Field(alias="macdHistogram", default=None)
    atr: Optional[float] = None
    vwap: Optional[float] = None
    supertrend_signal: Optional[str] = Field(alias="supertrendSignal", default=None)
    pattern: str = "NONE"
    support1: Optional[float] = None
    resistance1: Optional[float] = None
    stop_loss: Optional[float] = Field(default=None, alias="stopLoss")
    take_profit: Optional[float] = Field(default=None, alias="takeProfit")
    timeframe_analysis: dict[str, Any] = Field(default_factory=dict, alias="timeframeAnalysis")
    strategy_weights: dict[str, float] = Field(default_factory=dict, alias="strategyWeights")
    signal_strength: Optional[str] = Field(alias="signalStrength", default=None)
    snapshot_time: datetime | None = Field(default=None, alias="snapshotTime")
    run_id: Optional[str] = Field(default=None, alias="runId")
    origin: Optional[str] = None
    candles: list[Candle] = Field(default_factory=list)

    @field_validator("snapshot_time", mode="before")
    @classmethod
    def parse_snapshot_time(cls, value):
        return _parse_datetime_value(value)
