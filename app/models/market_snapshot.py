from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MarketSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")

    symbol: str
    symbol_token: str = Field(alias="symbolToken")
    exchange: str = ""
    timeframe: str
    price: float = Field(gt=0)
    trend: str
    trend_strength: str = Field(alias="trendStrength")
    market_regime: str = Field(alias="marketRegime")
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
    signal_strength: Optional[str] = Field(alias="signalStrength", default=None)
    snapshot_time: datetime = Field(alias="snapshotTime")
