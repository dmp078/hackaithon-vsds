from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import Prediction, QuestionItem


class QuestionSolver(ABC):
    @abstractmethod
    def solve(self, question: QuestionItem) -> Prediction:
        raise NotImplementedError
