import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import Settings
from app.models.ai_decision import AIDecision

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, settings: Settings):
        from langchain_ollama import ChatOllama

        self._settings = settings
        self._model = ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.ollama_temperature,
            format="json",
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4), reraise=True)
    async def decide(self, prompt: str) -> AIDecision:
        response = await self._model.ainvoke([
            SystemMessage(content="Return only valid JSON with decision, confidence, and reason."),
            HumanMessage(content=prompt),
        ])
        content: Any = response.content
        if isinstance(content, list):
            content = "".join(str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in content)
        try:
            return AIDecision.model_validate_json(str(content))
        except Exception:
            logger.exception("ollama_invalid_json")
            raise ValueError("Ollama returned an invalid AI decision JSON payload")
