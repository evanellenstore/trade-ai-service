from datetime import datetime, timezone

import pytest

from app.models.market_snapshot import MarketSnapshot
from app.models.signal_generated import SignalGenerated
from app.models.trading_state import TradingState


@pytest.fixture
def signal() -> SignalGenerated:
    return SignalGenerated(
        signalId="SIG-001", symbol="VEDL-EQ", symbolToken="3063", timeframe="ONE_MINUTE",
        strategyName="RSI", signal="BUY", confidence=95, price=262.6,
        reason="RSI triggered BUY with ADX trend confirmation",
        timestamp="2026-09-14T14:15:31.842096Z",
    )


@pytest.fixture
def snapshot() -> MarketSnapshot:
    return MarketSnapshot(
        symbol="VEDL-EQ", symbolToken="3063", exchange="NSE_CM", timeframe="ONE_MINUTE",
        price=262.6, trend="BULLISH", trendStrength="STRONG", marketRegime="TRENDING",
        volumeSpike=False, rsi14=55, adx=31, ema20=260, ema50=258, ema100=255, ema200=245,
        macd=1.2, macdSignal=0.9, macdHistogram=0.3, atr=14.5, vwap=261.3,
        supertrendSignal="BUY", pattern="NONE", support1=258, resistance1=272,
        signalStrength="HIGH", snapshotTime=datetime.fromisoformat("2026-09-14T14:15:31.842096+00:00"),
    )


@pytest.fixture
def state(signal, snapshot) -> TradingState:
    return TradingState.from_events(signal, snapshot)
