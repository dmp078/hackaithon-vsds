from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import QuestionItem


class LLMProvider(ABC):
    name: str

    def ensure_healthy(self) -> None:
        return None

    @abstractmethod
    def generate(self, question: QuestionItem, prompt: str) -> str:
        raise NotImplementedError
