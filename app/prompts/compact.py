from __future__ import annotations

from app.models import QuestionItem


def build(question: QuestionItem) -> tuple[str, str]:
    choice_lines = "\n".join(f"[{index}] {choice}" for index, choice in enumerate(question.choices))
    max_index = len(question.choices) - 1
    prompt = (
        "Chọn đúng một phương án cho câu hỏi trắc nghiệm sau.\n"
        "Chỉ trả về JSON hợp lệ theo schema:\n"
        '{"selected_index": <integer>}\n\n'
        f"selected_index bắt đầu từ 0 và phải nằm trong khoảng 0 đến {max_index}.\n\n"
        f"Câu hỏi:\n{question.question}\n\n"
        f"Các phương án:\n{choice_lines}"
    )
    return prompt, prompt

