from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import QuestionItem
from app.retrieval.models import RetrievedDocument


class BaseReranker(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def rerank(
        self,
        question: QuestionItem,
        candidates: list[RetrievedDocument],
        *,
        top_k: int,
    ) -> list[RetrievedDocument]:
        raise NotImplementedError
