from __future__ import annotations

from app.models import QuestionItem
from app.prompts.registry import build_prompt_variants_for_version, resolve_prompt_version


def test_baseline_prompt_preserves_existing_style() -> None:
    question = QuestionItem(qid="q1", question="Thủ đô Việt Nam?", choices=["Huế", "Hà Nội"])

    primary, full = build_prompt_variants_for_version(question, "baseline", category="general")

    assert "Bạn là hệ thống giải câu hỏi trắc nghiệm." in primary
    assert "Thủ đô Việt Nam?" in full


def test_compact_prompt_supports_dynamic_choice_count() -> None:
    question = QuestionItem(qid="q1", question="Chọn số.", choices=[str(index) for index in range(11)])

    primary, full = build_prompt_variants_for_version(question, "compact", category="general")

    assert "selected_index bắt đầu từ 0 và phải nằm trong khoảng 0 đến 10." in primary
    assert "[10] 10" in primary
    assert primary == full


def test_routed_prompt_selects_category_specific_versions() -> None:
    assert resolve_prompt_version("routed", "reading_comprehension") == "reading_comprehension"
    assert resolve_prompt_version("routed", "mathematics") == "stem"
    assert resolve_prompt_version("routed", "physics_engineering") == "stem"
    assert resolve_prompt_version("routed", "chemistry") == "stem"
    assert resolve_prompt_version("routed", "economics_finance") == "stem"
    assert resolve_prompt_version("routed", "history") == "compact"
