import json

from app.llm.ollama_client import OllamaClient
from app.models.trading_state import TradingState


class DecisionAgent:
    def __init__(self, ollama: OllamaClient):
        self._ollama = ollama

    async def __call__(self, state: TradingState) -> dict[str, object]:
        prompt = (
            "Evaluate this trading context as an advisor. Do not execute trades, calculate quantity, or apply risk rules. "
            "Return JSON only: {\"decision\":\"BUY|SELL|HOLD\",\"confidence\":0,\"reason\":\"...\"}. "
            f"Context: {json.dumps({'state': state.analysis_context(), 'market': state.market_analysis, 'technical': state.technical_analysis, 'strategy': state.strategy_analysis}, default=str)}"
        )
        result = await self._ollama.decide(prompt)
        return result.model_dump()
