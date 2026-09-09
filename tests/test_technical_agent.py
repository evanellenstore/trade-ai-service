from app.agents.technical_agent import technical_agent


def test_technical_agent_reports_neutral_equal_indicators(state):
    neutral_state = state.model_copy(update={
        "ema20": 1294.9,
        "ema50": 1294.9,
        "macd_histogram": 0.0,
        "rsi14": 0.0,
        "adx": 0.0,
        "supertrend_signal": "SELL",
        "pattern": "NONE",
        "volume_spike": False,
    })

    analysis = technical_agent(neutral_state)["technical_analysis"]

    assert "EMA alignment is neutral" in analysis
    assert "MACD histogram is neutral" in analysis
    assert "RSI 0.0" in analysis
    assert "ADX 0.0" in analysis
    assert "supertrend is SELL" in analysis