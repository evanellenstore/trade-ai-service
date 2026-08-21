from app.models.trading_state import TradingState


def strategy_agent(state: TradingState) -> dict[str, str]:
    market_aligned = state.signal.upper() == state.trend.upper() or state.trend.upper() == "SIDEWAYS"
    return {"strategy_analysis": (
        f"{state.strategy_name} strategy proposes {state.signal.upper()} with "
        f"{state.strategy_confidence:.0f}% confidence. Market alignment is "
        f"{'present' if market_aligned else 'conflicted'}; technical evidence must confirm before action."
    )}
