from app.models.trading_state import TradingState


def strategy_agent(state: TradingState) -> dict[str, object]:

    alignment = False

    if state.signal:

        alignment = (
            state.trend.upper() == state.signal.upper()
            or state.trend.upper() == "SIDEWAYS"
        )

    return {
        "strategy_analysis": {
            "strategy_name": state.strategy_name,
            "strategy_signal": state.signal,
            "strategy_confidence": state.strategy_confidence,
            "signal_strength": state.signal_strength,
            "market_alignment": alignment
        }
    }
