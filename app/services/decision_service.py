import logging

from app.config.settings import Settings
from app.graph.trading_graph import build_trading_graph
from app.kafka.producer import KafkaProducer
from app.models.ai_decision import AIDecisionEvent
from app.models.market_snapshot import MarketSnapshot
from app.models.signal_generated import SignalGenerated
from app.models.trading_state import TradingState

logger = logging.getLogger(__name__)


class DecisionService:
    def __init__(self, settings: Settings, producer: KafkaProducer, decision_agent):
        self._settings = settings
        self._producer = producer
        self._graph = build_trading_graph(decision_agent)

    async def evaluate(self, signal: SignalGenerated, snapshot: MarketSnapshot) -> AIDecisionEvent:
        # The Kafka consumer calls this method after receiving both matching events.
        # Build the trading state, run the AI graph, and map its output to a domain event.
        # Publishing that event allows downstream services to consume the AI decision.
        state = TradingState.from_events(signal, snapshot)
        print(f" ********************* Trading state created: {state}")

        # ainvoke() asynchronously executes the compiled LangGraph from START to END.
        # Each node receives the current TradingState and returns its analysis for the next node.
        # LangGraph waits for all nodes, including the Ollama-backed decision_agent, and returns the final state.
        result = await self._graph.ainvoke(state)
        decision = AIDecisionEvent(
            signalId=signal.signal_id,
            symbol=signal.symbol,
            strategy=signal.strategy_name,
            decision=result["decision"],
            confidence=result["confidence"],
            reason=result["reason"],
            aiVersion=self._settings.ai_version,
        )
        # Publish the completed decision so broker, portfolio, and monitoring services can react to it.
        await self._producer.publish(self._settings.ai_decision_topic, signal.symbol, decision)
        logger.info("ai_decision_created", extra={"signal_id": signal.signal_id, "decision": decision.decision})
        return decision
