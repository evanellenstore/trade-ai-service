import json

from app.llm.ollama_client import OllamaClient
from app.models.trading_state import TradingState


class DecisionAgent:

    def __init__(self, ollama: OllamaClient):
        self._ollama = ollama

    async def __call__(self, state: TradingState) -> dict[str, object]:

        payload = {
            "market": state.market_analysis,
            "technical": state.technical_analysis,
            "strategy": state.strategy_analysis,
        }

        prompt = f"""
You are an expert stock market trading advisor.

Your responsibility is to analyze the provided market, technical and strategy data and provide a trading recommendation.

IMPORTANT RULES:

- Never execute trades.
- Never place orders.
- Never calculate quantity.
- Never perform position sizing.
- Never perform risk management.
- Use only the provided data.
- SuperTrend has the highest priority.
- EMA alignment is highly important.
- MACD confirms momentum.
- ADX indicates trend strength.
- RSI indicates overbought or oversold conditions.
- VWAP indicates intraday bias.
- Candlestick patterns increase confidence.
- Volume spikes increase confidence.
- Support and resistance should be considered.
- Strategy output should be considered.
- If signals strongly conflict, return HOLD.

DECISION GUIDELINES:

Strong BUY Conditions:
- SuperTrend = BUY
- EMA alignment = BULLISH
- MACD = BULLISH
- Price above VWAP
- Trend = UP

Strong SELL Conditions:
- SuperTrend = SELL
- EMA alignment = BEARISH
- MACD = BEARISH
- Price below VWAP
- Trend = DOWN

HOLD Conditions:
- Mixed or conflicting signals
- Weak trend (low ADX)
- Sideways or ranging market
- Insufficient confirmation

CONFIDENCE SCALE:

90-100 : Very Strong Signal
80-89  : Strong Signal
70-79  : Good Signal
60-69  : Moderate Signal
50-59  : Weak Signal

Return ONLY valid JSON.

Expected Output:

{{
    "decision": "BUY|SELL|HOLD",
    "confidence": 0,
    "reason": "Short technical explanation"
}}

Trading Context:

{json.dumps(payload, indent=2, default=str)}
"""

        print(f"------------------------- Decision Agent Prompt: {prompt}")
        result = await self._ollama.decide(prompt)

        if hasattr(result, "model_dump"):
            return result.model_dump()
        
        print(f"------------------------- Decision Agent Result: {result}")

        return result