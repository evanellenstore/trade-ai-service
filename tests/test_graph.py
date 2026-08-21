import pytest

from app.graph.trading_graph import build_trading_graph


class FakeDecisionAgent:
    async def __call__(self, state):
        assert state.market_analysis
        assert state.technical_analysis
        assert state.strategy_analysis
        return {"decision": "BUY", "confidence": 87, "reason": "Aligned test evidence"}


@pytest.mark.asyncio
async def test_graph_runs_agents_in_order(state):
    result = await build_trading_graph(FakeDecisionAgent()).ainvoke(state)

    assert result["decision"] == "BUY"
    assert result["confidence"] == 87
    assert "Aligned" in result["reason"]
