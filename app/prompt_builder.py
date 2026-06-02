from __future__ import annotations

from app.models import QuestionItem


def build_prompt(question: QuestionItem) -> str:
    choice_lines = "\n".join(f"[{index}] {choice}" for index, choice in enumerate(question.choices))
    max_index = len(question.choices) - 1
    return (
        "Bạn là hệ thống giải câu hỏi trắc nghiệm.\n\n"
        "Hãy đọc kỹ toàn bộ câu hỏi và tất cả các phương án.\n"
        "Chọn chính xác một phương án phù hợp nhất.\n\n"
        "Quy tắc bắt buộc:\n"
        "- Chỉ trả về một JSON object hợp lệ.\n"
        "- selected_index là chỉ số của phương án, bắt đầu từ 0.\n"
        "- Không trả lời bằng chữ cái.\n"
        "- Không giải thích.\n"
        "- Không thêm markdown.\n"
        "- Không thêm văn bản bên ngoài JSON.\n"
        f"- selected_index phải nằm trong khoảng từ 0 đến {max_index}.\n\n"
        f"Câu hỏi:\n{question.question}\n\n"
        f"Các phương án:\n{choice_lines}\n\n"
        'Schema đầu ra:\n{"selected_index": <integer>}'
    )


def build_repair_prompt(previous_response: str, max_index: int, original_prompt: str) -> str:
    return (
        "Phản hồi trước không hợp lệ.\n"
        "Dưới đây là câu hỏi gốc và các phương án. Hãy đọc lại và trả về đúng schema.\n\n"
        f"{original_prompt}\n\n"
        "Phản hồi trước bị loại vì không hợp lệ.\n"
        "Chỉ trả về JSON theo schema sau:\n"
        f'{{"selected_index": <integer từ 0 đến {max_index}>}}\n\n'
        f"Phản hồi trước:\n{previous_response}"
    )
