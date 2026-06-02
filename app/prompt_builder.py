from __future__ import annotations

import re

from app.models import QuestionItem


def build_prompt(question: QuestionItem) -> str:
    primary_prompt, _ = build_prompt_variants(question)
    return primary_prompt


def build_prompt_variants(question: QuestionItem) -> tuple[str, str]:
    full_prompt = _compose_prompt(question.question, question.choices)
    reduced_question = _build_reduced_question_text(question)
    primary_prompt = _compose_prompt(reduced_question, question.choices)
    return primary_prompt, full_prompt


def _compose_prompt(question_text: str, choices: list[str]) -> str:
    choice_lines = "\n".join(f"[{index}] {choice}" for index, choice in enumerate(choices))
    max_index = len(choices) - 1
    return (
        "Bạn là hệ thống giải câu hỏi trắc nghiệm.\n\n"
        "Hãy đọc kỹ toàn bộ câu hỏi và tất cả các phương án.\n"
        "Chọn chính xác một phương án phù hợp nhất.\n\n"
        "Quy tắc bắt buộc:\n"
        "- Nếu không chắc chắn, vẫn phải chọn đúng một phương án có khả năng cao nhất.\n"
        "- Chỉ trả về một JSON object hợp lệ.\n"
        "- selected_index là chỉ số của phương án, bắt đầu từ 0.\n"
        "- Không trả lời bằng chữ cái.\n"
        "- Không giải thích.\n"
        "- Không thêm markdown.\n"
        "- Không thêm văn bản bên ngoài JSON.\n"
        f"- selected_index phải nằm trong khoảng từ 0 đến {max_index}.\n\n"
        f"Câu hỏi:\n{question_text}\n\n"
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


def _build_reduced_question_text(question: QuestionItem) -> str:
    raw_text = question.question
    if len(raw_text) < 120:
        return raw_text

    context_text, focus_question = _split_context_and_focus(raw_text)
    if not context_text or not focus_question:
        return raw_text

    chunks = _split_context_chunks(context_text)
    if len(chunks) < 3:
        return raw_text

    selected_chunks = _select_relevant_chunks(chunks, focus_question, question.choices)
    if len(selected_chunks) < 1:
        return raw_text

    reduced_text = (
        "Đoạn thông tin đã rút gọn theo mức độ liên quan:\n"
        + "\n\n".join(selected_chunks)
        + f"\n\nCâu hỏi: {focus_question}"
    )
    if len(reduced_text) >= len(raw_text):
        return raw_text
    return reduced_text


def _split_context_and_focus(raw_text: str) -> tuple[str | None, str | None]:
    if "Câu hỏi:" in raw_text:
        context_text, focus_question = raw_text.rsplit("Câu hỏi:", 1)
        return context_text.strip(), focus_question.strip()
    return None, None


def _split_context_chunks(context_text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", context_text) if chunk.strip()]
    if len(chunks) >= 2:
        return chunks
    lines = [line.strip() for line in context_text.splitlines() if line.strip()]
    return lines


def _select_relevant_chunks(chunks: list[str], focus_question: str, choices: list[str]) -> list[str]:
    query_tokens = _tokenize(focus_question + " " + " ".join(choices))
    scored_chunks: list[tuple[float, int, str]] = []
    for index, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        chunk_tokens = _tokenize(chunk)
        overlap = len(query_tokens & chunk_tokens)
        choice_phrase_hits = sum(1 for choice in choices if len(choice) > 6 and choice.lower() in chunk_lower)
        score = overlap + choice_phrase_hits * 3
        if "tiêu đề:" in chunk_lower or "title:" in chunk_lower:
            score += 0.5
        scored_chunks.append((score, index, chunk))

    top_chunks = [item for item in sorted(scored_chunks, key=lambda item: (-item[0], item[1])) if item[0] > 0][:3]
    if not top_chunks:
        return []
    return [chunk for _, _, chunk in sorted(top_chunks, key=lambda item: item[1])]


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[0-9A-Za-zÀ-ỹ]+", text.lower())
        if len(token) >= 2
    }
