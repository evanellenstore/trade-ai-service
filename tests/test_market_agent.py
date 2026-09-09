from app.agents.market_agent import market_agent


def test_market_agent_reports_price_at_vwap(state):
    market_state = state.model_copy(update={
        "price": 1294.9,
        "vwap": 1294.9,
        "support1": 1294.9,
        "resistance1": 1294.9,
        "atr": 17.65457067037366,
    })

    analysis = market_agent(market_state)["market_analysis"]

    assert "price is at VWAP" in analysis
    assert "support 1294.90, resistance 1294.90" in analysis
    assert "ATR 17.65" in analysis


def test_market_agent_reports_unavailable_market_values(state):
    market_state = state.model_copy(update={
        "vwap": None,
        "support1": None,
        "resistance1": None,
        "atr": None,
    })

    analysis = market_agent(market_state)["market_analysis"]

    assert "price is unavailable relative to VWAP" in analysis
    assert "support unavailable, resistance unavailable" in analysis
    assert "ATR unavailable" in analysis