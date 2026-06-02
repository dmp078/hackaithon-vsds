from __future__ import annotations

import json

import httpx

from app.config import AppConfig
from app.models import QuestionItem
from app.providers.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    name = "openai-compatible"

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.client = httpx.Client(
            timeout=config.ollama_timeout_seconds,
            headers={"Authorization": f"Bearer {config.openai_compatible_api_key}"},
        )

    def ensure_healthy(self) -> None:
        try:
            response = self.client.get(f"{self.config.openai_compatible_base_url.rstrip('/')}/models")
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"OpenAI-compatible health check timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"OpenAI-compatible health check failed: {exc}") from exc

    def generate(self, question: QuestionItem, prompt: str) -> str:
        payload = {
            "model": self.config.openai_compatible_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.ollama_temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "mcq_response",
                    "schema": {
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
                },
            },
        }
        try:
            response = self.client.post(
                f"{self.config.openai_compatible_base_url.rstrip('/')}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"OpenAI-compatible request timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            body = exc.response.text if exc.response is not None else str(exc)
            raise RuntimeError(f"OpenAI-compatible request failed: {body}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenAI-compatible response: {json.dumps(data, ensure_ascii=False)}") from exc
