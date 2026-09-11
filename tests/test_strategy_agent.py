from app.agents.strategy_agent import strategy_agent


def test_buy_signal_with_bearish_trend_and_sell_supertrend_is_conflict(state):
    bearish_state = state.model_copy(update={
        "trend": "BEARISH",
        "supertrend_signal": "SELL",
        "rsi14": 15.8,
    })

    analysis = strategy_agent(bearish_state)["strategy_analysis"]

    assert analysis["trend"] == "BEARISH"
    assert analysis["supertrend"] == "SELL"
    assert analysis["supertrend_conflict"] is True
    assert analysis["validation_result"] == "CONFLICT"


def test_sell_signal_with_bullish_supertrend_is_conflict(state):
    bullish_state = state.model_copy(update={
        "signal": "SELL",
        "trend": "BULLISH",
        "supertrend_signal": "BUY",
    })

    analysis = strategy_agent(bullish_state)["strategy_analysis"]

    assert analysis["supertrend_conflict"] is True
    assert analysis["validation_result"] == "CONFLICT"