from app.models.trading_state import TradingState


def technical_agent(state: TradingState) -> dict[str, str]:
    ema = "unavailable"
    if state.ema20 is not None and state.ema50 is not None:
        ema = "bullish" if state.ema20 >= state.ema50 else "bearish"
    rsi = f"RSI {state.rsi14:.1f}" if state.rsi14 is not None else "RSI unavailable"
    macd = "positive" if (state.macd_histogram or 0) >= 0 else "negative"
    adx = f"ADX {state.adx:.1f}" if state.adx is not None else "ADX unavailable"
    return {"technical_analysis": (
        f"EMA alignment is {ema}; {rsi}; MACD histogram is {macd}; {adx}; "
        f"supertrend is {state.supertrend_signal or 'unavailable'}; pattern is {state.pattern}; "
        f"volume spike is {'present' if state.volume_spike else 'absent'}."
    )}
