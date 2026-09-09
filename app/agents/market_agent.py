from app.models.trading_state import TradingState


def market_agent(state: TradingState) -> dict[str, object]:

    vwap_position = "ABOVE"

    if state.vwap is not None and state.price < state.vwap:
        vwap_position = "BELOW"

    if state.atr is None:
        volatility = "UNKNOWN"
    elif state.atr >= 20:
        volatility = "HIGH"
    elif state.atr >= 10:
        volatility = "MEDIUM"
    else:
        volatility = "LOW"

    return {
        "market_analysis": {
            "symbol": state.symbol,
            "price": state.price,
            "trend": state.trend,
            "trend_strength": state.trend_strength,
            "market_regime": state.market_regime,
            "vwap_position": vwap_position,
            "volatility": volatility,
            "atr": state.atr,
            "support": state.support1,
            "resistance": state.resistance1
        }
    }
