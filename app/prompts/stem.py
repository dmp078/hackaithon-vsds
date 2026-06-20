from __future__ import annotations

from app.models import QuestionItem


def build(question: QuestionItem) -> tuple[str, str]:
    choice_lines = "\n".join(f"[{index}] {choice}" for index, choice in enumerate(question.choices))
    max_index = len(question.choices) - 1
    prompt = (
        "Giải bài trắc nghiệm cẩn thận, kiểm tra công thức và đơn vị nếu có.\n"
        "Chọn một phương án đúng nhất.\n"
        "Chỉ trả về JSON hợp lệ, không trình bày lời giải.\n"
        f'schema: {{"selected_index": <integer từ 0 đến {max_index}>}}\n\n'
        f"Câu hỏi:\n{question.question}\n\n"
        f"Các phương án:\n{choice_lines}"
    )
    return prompt, prompt

