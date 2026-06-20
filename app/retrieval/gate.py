from __future__ import annotations

import re

from app.config import AppConfig
from app.models import QuestionItem


RETRIEVAL_CATEGORIES = {
    "mathematics",
    "physics_engineering",
    "chemistry",
    "economics_finance",
    "computer_science",
    "law_safety",
}


class RetrievalGate:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def should_retrieve(self, question: QuestionItem) -> bool:
        if self.config.retrieval_mode != "on":
            return False

        if question.category not in RETRIEVAL_CATEGORIES:
            return False

        normalized = question.question.lower()
        if len(normalized) < 50:
            return False

        if re.fullmatch(r"[\d\s+\-*/().,=]+", question.question.strip()):
            return False

        if re.search(r"\b\d+\s*[\+\-\*/]\s*\d+\b", normalized):
            return False

        helpful_keywords = (
            "công thức",
            "định nghĩa",
            "định luật",
            "nguyên lý",
            "khái niệm",
            "cấu trúc dữ liệu",
            "thuật toán",
            "lãi suất",
            "gdp",
            "delta",
        )
        return any(keyword in normalized for keyword in helpful_keywords)
