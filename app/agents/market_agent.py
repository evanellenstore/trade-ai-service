from app.models.trading_state import TradingState


def market_agent(state: TradingState) -> dict[str, str]:
    vwap_position = "above VWAP" if state.vwap is not None and state.price >= state.vwap else "below VWAP"
    volatility = f"ATR {state.atr:.2f}" if state.atr is not None else "ATR unavailable"
    levels = f"support {state.support1}, resistance {state.resistance1}"
    return {"market_analysis": (
        f"Trend is {state.trend} with {state.trend_strength} strength in a {state.market_regime} regime; "
        f"price is {vwap_position}. Key levels: {levels}. Volatility: {volatility}."
    )}
