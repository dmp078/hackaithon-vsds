from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class QuestionItem(BaseModel):
    qid: str
    question: str
    choices: list[str]

    @field_validator("qid", "question")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value must not be empty")
        return value

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, value: list[str]) -> list[str]:
        if len(value) < 2:
            raise ValueError("choices must contain at least 2 items")
        if any(not isinstance(choice, str) or not choice.strip() for choice in value):
            raise ValueError("choices must contain non-empty strings")
        return value


class Prediction(BaseModel):
    qid: str
    selected_index: int
    answer: str | None = None
    provider: str
    latency_ms: float
    raw_response: str | None = None
    error: str | None = None
    used_fallback: bool = False


class BenchmarkSummary(BaseModel):
    input_file: str
    output_file: str
    total_questions: int
    successful_predictions: int
    failed_predictions: int
    fallback_predictions: int
    total_latency_ms: float
    average_latency_ms: float
    solver_mode: str
    provider: str
    model: str | None
    invalid_records: int = Field(default=0)
