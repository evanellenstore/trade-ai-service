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
        state = TradingState.from_events(signal, snapshot)
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
        await self._producer.publish(self._settings.ai_decision_topic, signal.symbol, decision)
        logger.info("ai_decision_created", extra={"signal_id": signal.signal_id, "decision": decision.decision})
        return decision
