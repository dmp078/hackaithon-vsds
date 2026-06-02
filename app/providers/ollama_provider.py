from __future__ import annotations

import json

import httpx

from app.config import AppConfig
from app.models import QuestionItem
from app.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.client = httpx.Client(timeout=config.ollama_timeout_seconds)

    def ensure_healthy(self) -> None:
        url = f"{self.config.ollama_base_url.rstrip('/')}/api/tags"
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"Ollama health check timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama health check failed: {exc}") from exc

    def generate(self, question: QuestionItem, prompt: str) -> str:
        url = f"{self.config.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.config.ollama_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": self.config.ollama_think,
            "format": {
                "type": "object",
                "properties": {
                    "selected_index": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": len(question.choices) - 1,
                    }
                },
                "required": ["selected_index"],
            },
            "options": {
                "temperature": self.config.ollama_temperature,
                "num_ctx": self.config.ollama_num_ctx,
                "num_predict": self.config.ollama_num_predict,
            },
        }
        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"Ollama request timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            body = exc.response.text if exc.response is not None else str(exc)
            raise RuntimeError(f"Ollama request failed: {body}") from exc

        data = response.json()
        message = data.get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise RuntimeError(f"Unexpected Ollama response: {json.dumps(data, ensure_ascii=False)}")
        return content
