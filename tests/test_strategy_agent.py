import pytest

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


def test_volume_confirmation_is_required_for_trade_approval(state):
    analysis = strategy_agent(state)["strategy_analysis"]

    assert analysis["volume_confirmed"] is False
    assert analysis["phase1_filter"] == "VOLUME"
    assert analysis["approved_signal"] == "HOLD"


def test_risk_reward_filter_rejects_unfavorable_setup(state):
    filtered_state = state.model_copy(update={
        "volume_spike": True,
        "stop_loss": 262.0,
        "take_profit": 263.0,
    })

    analysis = strategy_agent(filtered_state)["strategy_analysis"]

    assert analysis["risk_reward"] == pytest.approx(2 / 3)
    assert analysis["risk_reward_passed"] is False
    assert analysis["phase1_filter"] == "RISK_REWARD"
    assert analysis["approved_signal"] == "HOLD"


def test_multi_timeframe_consensus_rejects_countertrend_signal(state):
    filtered_state = state.model_copy(update={
        "volume_spike": True,
        "timeframe_analysis": {
            "FIVE_MINUTE": {"signal": "SELL"},
            "FIFTEEN_MINUTE": {"signal": "SELL"},
        },
    })

    analysis = strategy_agent(filtered_state)["strategy_analysis"]

    assert analysis["timeframe_consensus"] is False
    assert analysis["phase1_filter"] == "TIMEFRAME"
    assert analysis["approved_signal"] == "HOLD"


def test_strategy_weights_change_component_contribution(state):
    weighted_state = state.model_copy(update={
        "volume_spike": True,
        "strategy_weights": {"volume": 5},
    })

    analysis = strategy_agent(weighted_state)["strategy_analysis"]

    assert analysis["bullish_score"] == 13
    assert analysis["approved_signal"] == "BUY"