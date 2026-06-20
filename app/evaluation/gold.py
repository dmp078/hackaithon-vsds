from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, field_validator

from app.models import QuestionItem


class GoldQuestion(BaseModel):
    qid: str
    question: str
    choices: list[str]
    gold_index: int
    gold_answer: str | None = None
    category: str = "uncategorized"
    verification_status: str | None = None
    recommended_use: str | None = None

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, value: list[str]) -> list[str]:
        if len(value) < 2:
            raise ValueError("choices must contain at least 2 items")
        if any(not isinstance(choice, str) or not choice.strip() for choice in value):
            raise ValueError("choices must contain non-empty strings")
        return value

    def to_question_item(self) -> QuestionItem:
        return QuestionItem(
            qid=self.qid,
            question=self.question,
            choices=self.choices,
            category=self.category,
        )


def load_gold_questions(path: Path) -> list[GoldQuestion]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("gold validation file must contain a JSON array")

    questions = [GoldQuestion.model_validate(item) for item in payload]
    for question in questions:
        if question.gold_index < 0 or question.gold_index >= len(question.choices):
            raise ValueError(
                f"gold_index out of range for {question.qid}: "
                f"{question.gold_index} not in 0..{len(question.choices) - 1}"
            )
    return questions

