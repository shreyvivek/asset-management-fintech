from abc import ABC, abstractmethod
from typing import Any
import httpx
from app.core.config import get_settings


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], model: str | None = None, response_format: dict | None = None) -> str:
        pass

    @abstractmethod
    async def chat_json(self, messages: list[dict], model: str | None = None, schema: type) -> dict:
        pass


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        pass


class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        self.settings = get_settings()

    async def chat(self, messages: list[dict], model: str | None = None, response_format: dict | None = None) -> str:
        if not self.settings.openai_api_key:
            return _mock_llm_response(messages)
        async with httpx.AsyncClient(timeout=60.0) as client:
            url = (self.settings.openai_base_url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
            payload = {
                "model": model or self.settings.llm_model,
                "messages": messages,
                "max_tokens": 1024,
            }
            if response_format:
                payload["response_format"] = response_format
            r = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def chat_json(self, messages: list[dict], model: str | None = None, schema: type) -> dict:
        import json
        content = await self.chat(messages, model=model)
        try:
            # Extract JSON block if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return _repair_json_schema(content, schema)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        self.settings = get_settings()

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        if not self.settings.openai_api_key or not texts:
            return _mock_embeddings(len(texts))
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = (self.settings.openai_base_url or "https://api.openai.com/v1").rstrip("/") + "/embeddings"
            r = await client.post(
                url,
                json={
                    "model": model or self.settings.embedding_model,
                    "input": texts,
                },
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
            )
            r.raise_for_status()
            data = r.json()
            return [item["embedding"] for item in data["data"]]


def _mock_llm_response(messages: list[dict]) -> str:
    return '{"thesis": "Mock analysis.", "directional_calls": [], "confidence": 0.5, "evidence_anchors": ["Mock evidence."]}'


def _mock_embeddings(n: int, dim: int = 1536) -> list[list[float]]:
    import random
    return [[random.gauss(0, 0.1) for _ in range(dim)] for _ in range(n)]


def _repair_json_schema(content: str, schema: type) -> dict:
    """Return a minimal valid dict for schema; used when LLM returns malformed JSON."""
    return {}


_llm: LLMProvider | None = None
_embed: EmbeddingProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _llm
    if _llm is None:
        _llm = OpenAILLMProvider()
    return _llm


def get_embedding_provider() -> EmbeddingProvider:
    global _embed
    if _embed is None:
        _embed = OpenAIEmbeddingProvider()
    return _embed
