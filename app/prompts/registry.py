from __future__ import annotations

from app.models import QuestionItem
from app.prompts import baseline, compact, reading_comprehension, stem


STEM_CATEGORIES = {
    "mathematics",
    "physics_engineering",
    "chemistry",
    "economics_finance",
}


def resolve_prompt_version(prompt_version: str, category: str | None) -> str:
    if prompt_version != "routed":
        return prompt_version
    if category == "reading_comprehension":
        return "reading_comprehension"
    if category in STEM_CATEGORIES:
        return "stem"
    return "compact"


def build_prompt_variants_for_version(
    question: QuestionItem,
    prompt_version: str,
    category: str | None = None,
) -> tuple[str, str]:
    resolved_version = resolve_prompt_version(prompt_version, category)
    if resolved_version == "baseline":
        return baseline.build(question)
    if resolved_version == "compact":
        return compact.build(question)
    if resolved_version == "reading_comprehension":
        return reading_comprehension.build(question)
    if resolved_version == "stem":
        return stem.build(question)
    raise ValueError(f"Unsupported prompt version: {prompt_version}")
