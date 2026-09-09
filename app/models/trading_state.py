from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.market_snapshot import MarketSnapshot
from app.models.signal_generated import SignalGenerated


INDICATOR_FIELDS = {
    "EMA_CROSSOVER": ("ema20", "ema50"),
    "MACD": ("macd",),
    "RSI": ("rsi14",),
    "SUPER_TREND": ("supertrend_signal",),
    "VWAP": ("vwap",),
    "ADX_DI": ("adx",),
}
PATTERNS = {
    "AscendingTriangle", "BearFlag", "BullFlag", "CupAndHandle", "DescendingTriangle",
    "DoubleBottom", "DoubleTop", "FallingWedge", "HeadAndShoulders",
    "InverseHeadAndShoulders", "Rectangle", "ResistanceBreakout", "RisingWedge", "NONE",
}


class TradingState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    signal_id: str
    symbol: str
    symbol_token: str
    timeframe: str
    strategy_name: str
    signal: str
    strategy_confidence: float
    signal_strength: Optional[str] = None
    price: float
    trend: str
    trend_strength: str
    market_regime: str
    volume_spike: bool = False
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema100: Optional[float] = None
    ema200: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    rsi14: Optional[float] = None
    adx: Optional[float] = None
    atr: Optional[float] = None
    vwap: Optional[float] = None
    supertrend_signal: Optional[str] = None
    support1: Optional[float] = None
    resistance1: Optional[float] = None
    pattern: str = "NONE"
    indicators: list[str] = Field(default_factory=list)
    market_analysis: dict[str, Any] = Field(default_factory=dict)
    technical_analysis: dict[str, Any] = Field(default_factory=dict)
    strategy_analysis: dict[str, Any] = Field(default_factory=dict)
    decision: Optional[str] = None
    confidence: Optional[int] = None
    reason: Optional[str] = None
    snapshot_time: Optional[datetime] = None
    signal_reason: str = ""

    @classmethod
    def from_events(cls, signal: SignalGenerated, snapshot: MarketSnapshot) -> "TradingState":
        print(f"------------------------- Trading state from_events called with signal: {signal}")
        print(f"------------------------- Trading state from_events called with snapshot: {snapshot}")
        data = snapshot.model_dump()
        # print(f" ============ ========== Trading state data initialized: {data}")
        for shared_field in ("symbol", "symbol_token", "timeframe", "price", "snapshot_time"):
            data.pop(shared_field, None)
            
       # print(f"============ ==========After popup Trading state data : {data}")  
        # create a new TradingState instance using the signal and snapshot data, excluding shared fields
        # The shared fields are removed from the snapshot data to avoid overwriting the values from the signal event, which are considered more relevant for the trading state.
        # The remaining fields from the snapshot are included in the TradingState to provide additional context for the AI decision-making process.
        # it is same like 
        state = cls(
            signal_id=signal.signal_id, 
            symbol=signal.symbol, 
            symbol_token=signal.symbol_token,
            timeframe=signal.timeframe, 
            strategy_name=signal.strategy_name, 
            signal=signal.signal,
            strategy_confidence=signal.confidence, 
            signal_reason=signal.reason, 
            price=snapshot.price,
            snapshot_time=snapshot.snapshot_time,
            **data,
        )
        
        print(f"============ ========== Trading state created: {state}")
        
        state.indicators = [
            name
            for name, fields in INDICATOR_FIELDS.items()
            if all(getattr(state, field) is not None for field in fields)
        ]
        
        print(f"============ ========== Trading state indicators: {state.indicators}")
        
        if state.pattern not in PATTERNS:
            state.pattern = "NONE"
        return state

    def analysis_context(self) -> dict[str, Any]:
        return self.model_dump(exclude={"market_analysis", "technical_analysis", "strategy_analysis"})
