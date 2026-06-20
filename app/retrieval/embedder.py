from __future__ import annotations

import json
from abc import ABC, abstractmethod

import httpx

from app.config import AppConfig


class TextEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class OllamaTextEmbedder(TextEmbedder):
    def __init__(self, config: AppConfig, *, model: str | None = None) -> None:
        self.config = config
        self.model = model or config.retrieval_embedding_model
        self.client = httpx.Client(timeout=config.ollama_timeout_seconds)

    def embed(self, text: str) -> list[float]:
        url = f"{self.config.ollama_base_url.rstrip('/')}/api/embed"
        payload = {"model": self.model, "input": text}
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings", [])
        if not embeddings:
            raise RuntimeError(f"Unexpected embedding response: {json.dumps(data, ensure_ascii=False)}")
        vector = embeddings[0]
        if not isinstance(vector, list):
            raise RuntimeError(f"Unexpected embedding vector: {json.dumps(data, ensure_ascii=False)}")
        return [float(value) for value in vector]
