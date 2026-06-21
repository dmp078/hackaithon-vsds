from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import QuestionItem
from app.strategies.models import StrategyExecutionContext, StrategyResult


class InferenceStrategy(ABC):
    name: str

    @abstractmethod
    def execute(
        self,
        question: QuestionItem,
        context: StrategyExecutionContext | None = None,
    ) -> StrategyResult:
        raise NotImplementedError
