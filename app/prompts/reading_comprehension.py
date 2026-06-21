from __future__ import annotations

from app.models import QuestionItem


def build(question: QuestionItem) -> tuple[str, str]:
    choice_lines = "\n".join(f"[{index}] {choice}" for index, choice in enumerate(question.choices))
    max_index = len(question.choices) - 1
    prompt = (
        "Chỉ dùng ngữ cảnh được cung cấp để chọn phương án đúng nhất.\n"
        "Đọc kỹ câu hỏi cuối, bỏ qua đoạn không liên quan.\n"
        "Chỉ trả về JSON hợp lệ, không giải thích.\n"
        f'schema: {{"selected_index": <integer từ 0 đến {max_index}>}}\n\n'
        f"Câu hỏi và ngữ cảnh:\n{question.question}\n\n"
        f"Các phương án:\n{choice_lines}"
    )
    return prompt, prompt
