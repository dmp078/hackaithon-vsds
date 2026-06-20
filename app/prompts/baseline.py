from __future__ import annotations

from app.models import QuestionItem
from app.prompt_builder import build_prompt_variants


def build(question: QuestionItem) -> tuple[str, str]:
    return build_prompt_variants(question)

