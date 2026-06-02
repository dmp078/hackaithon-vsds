from app.models import QuestionItem
from app.prompt_builder import build_prompt


def test_render_vietnamese_prompt_and_complete_question() -> None:
    question = QuestionItem(
        qid="q1",
        question="Thủ đô của Việt Nam là gì?",
        choices=["Hà Nội", "Huế"],
    )

    prompt = build_prompt(question)

    assert "Bạn là hệ thống giải câu hỏi trắc nghiệm." in prompt
    assert "Thủ đô của Việt Nam là gì?" in prompt


def test_render_every_choice_and_dynamic_max_index_for_two_choices() -> None:
    question = QuestionItem(
        qid="q1",
        question="Chọn đáp án đúng.",
        choices=["A", "B"],
    )

    prompt = build_prompt(question)

    assert "[0] A" in prompt
    assert "[1] B" in prompt
    assert "selected_index phải nằm trong khoảng từ 0 đến 1." in prompt


def test_support_ten_choices_without_assuming_four() -> None:
    choices = [str(index) for index in range(10)]
    question = QuestionItem(qid="q1", question="Chọn số lớn nhất.", choices=choices)

    prompt = build_prompt(question)

    assert "[9] 9" in prompt
    assert "selected_index phải nằm trong khoảng từ 0 đến 9." in prompt
