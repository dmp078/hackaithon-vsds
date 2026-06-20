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
    retrieval_snippets: list[str] | None = None,
) -> tuple[str, str]:
    resolved_version = resolve_prompt_version(prompt_version, category)
    if resolved_version == "baseline":
        primary, full = baseline.build(question)
    elif resolved_version == "compact":
        primary, full = compact.build(question)
    elif resolved_version == "reading_comprehension":
        primary, full = reading_comprehension.build(question)
    elif resolved_version == "stem":
        primary, full = stem.build(question)
    else:
        raise ValueError(f"Unsupported prompt version: {prompt_version}")
    return (
        _append_retrieval_context(primary, retrieval_snippets),
        _append_retrieval_context(full, retrieval_snippets),
    )


def _append_retrieval_context(prompt: str, retrieval_snippets: list[str] | None) -> str:
    if not retrieval_snippets:
        return prompt
    context_block = (
        "Ngữ cảnh tham khảo ngắn:\n"
        + "\n\n".join(retrieval_snippets)
        + "\n\nHãy ưu tiên ngữ cảnh này khi nó liên quan trực tiếp đến câu hỏi.\n\n"
    )
    marker = "Câu hỏi:\n"
    if marker in prompt:
        return prompt.replace(marker, context_block + marker, 1)
    marker = "Câu hỏi và ngữ cảnh:\n"
    if marker in prompt:
        return prompt.replace(marker, context_block + marker, 1)
    return context_block + prompt
