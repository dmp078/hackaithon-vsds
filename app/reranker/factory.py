from __future__ import annotations

from app.config import AppConfig
from app.reranker.base import BaseReranker
from app.reranker.noop import NoOpReranker


def build_reranker(config: AppConfig) -> BaseReranker | None:
    if config.retrieval_reranker_mode != "on":
        return None
    return NoOpReranker()
