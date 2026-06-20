from __future__ import annotations

from app.models import QuestionItem
from app.reranker.base import BaseReranker
from app.retrieval.models import RetrievedDocument


class NoOpReranker(BaseReranker):
    def is_available(self) -> bool:
        return False

    def rerank(
        self,
        question: QuestionItem,
        candidates: list[RetrievedDocument],
        *,
        top_k: int,
    ) -> list[RetrievedDocument]:
        return candidates[:top_k]
