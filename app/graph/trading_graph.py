from langgraph.graph import END, START, StateGraph

from app.agents.decision_agent import DecisionAgent
from app.agents.market_agent import market_agent
from app.agents.strategy_agent import strategy_agent
from app.agents.technical_agent import technical_agent
from app.models.trading_state import TradingState


def build_trading_graph(decision_agent: DecisionAgent):
    graph = StateGraph(TradingState)
    graph.add_node("market_agent", market_agent)
    graph.add_node("technical_agent", technical_agent)
    graph.add_node("strategy_agent", strategy_agent)
    graph.add_node("decision_agent", decision_agent)
    graph.add_edge(START, "market_agent")
    graph.add_edge("market_agent", "technical_agent")
    graph.add_edge("technical_agent", "strategy_agent")
    graph.add_edge("strategy_agent", "decision_agent")
    graph.add_edge("decision_agent", END)
    return graph.compile()
