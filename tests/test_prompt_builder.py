from app.models import QuestionItem
from app.prompt_builder import build_prompt, build_prompt_variants


def test_render_vietnamese_prompt_and_complete_question() -> None:
    question = QuestionItem(
        qid="q1",
        question="Thủ đô của Việt Nam là gì?",
        choices=["Hà Nội", "Huế"],
    )

    prompt = build_prompt(question)

    assert "Bạn là hệ thống giải câu hỏi trắc nghiệm." in prompt
    assert "Thủ đô của Việt Nam là gì?" in prompt
    assert "Nếu không chắc chắn, vẫn phải chọn đúng một phương án có khả năng cao nhất." in prompt


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


def test_long_prompt_variant_keeps_focus_and_relevant_excerpt() -> None:
    question = QuestionItem(
        qid="q_long",
        question=(
            "Đoạn thông tin:\n"
            "Đoạn 1: Nội dung không liên quan về khí hậu sa mạc.\n\n"
            "Đoạn 2: Friedrich Wilhelm I được gọi là vua chiến sĩ vì ông xây dựng quân đội Phổ hùng mạnh.\n\n"
            "Đoạn 3: Nội dung khác về thương mại đường biển.\n\n"
            "Câu hỏi: Tại sao Friedrich Wilhelm I được gọi là vua chiến sĩ?"
        ),
        choices=[
            "Vì ông cải cách tài chính",
            "Vì ông xây dựng quân đội Phổ hùng mạnh",
            "Vì ông kết hôn với công chúa Anh",
        ],
    )

    primary_prompt, full_prompt = build_prompt_variants(question)

    assert "Tại sao Friedrich Wilhelm I được gọi là vua chiến sĩ?" in primary_prompt
    assert "quân đội Phổ hùng mạnh" in primary_prompt
    assert len(primary_prompt) < len(full_prompt)
    assert "khí hậu sa mạc" in full_prompt
