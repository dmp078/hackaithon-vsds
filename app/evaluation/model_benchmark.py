from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from app.evaluation.metrics import percentile


def slugify_model_name(model_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", model_name.lower())
    return normalized.strip("_")


def load_submission_answers(path: Path) -> dict[str, str]:
    answers: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["qid", "answer"]:
            raise ValueError(f"Unexpected submission header in {path}: {reader.fieldnames}")
        for row in reader:
            qid = str(row["qid"])
            if qid in answers:
                raise ValueError(f"Duplicate qid in submission {path}: {qid}")
            answers[qid] = str(row["answer"])
    return answers


def compute_submission_disagreement(baseline_path: Path, candidate_path: Path) -> dict[str, Any]:
    baseline = load_submission_answers(baseline_path)
    candidate = load_submission_answers(candidate_path)
    if baseline.keys() != candidate.keys():
        missing_in_candidate = sorted(set(baseline) - set(candidate))
        missing_in_baseline = sorted(set(candidate) - set(baseline))
        raise ValueError(
            "Submission qid mismatch. "
            f"Missing in candidate: {missing_in_candidate[:5]}; "
            f"missing in baseline: {missing_in_baseline[:5]}"
        )

    changed_qids = sorted(qid for qid, answer in candidate.items() if baseline[qid] != answer)
    total_questions = len(candidate)
    changed_answers = len(changed_qids)
    return {
        "total_questions": total_questions,
        "changed_answers": changed_answers,
        "disagreement_rate": changed_answers / total_questions if total_questions else 0.0,
        "changed_qids": changed_qids,
    }


def build_question_profile_map(public_input_path: Path) -> dict[str, dict[str, Any]]:
    raw_records = json.loads(public_input_path.read_text(encoding="utf-8"))
    profiles: dict[str, dict[str, Any]] = {}
    for record in raw_records:
        qid = str(record["qid"])
        question = str(record["question"])
        choices = [str(choice) for choice in record["choices"]]
        profiles[qid] = {
            "category": infer_question_category(question, choices),
            "question_char_length": len(question),
            "choice_count": len(choices),
        }
    return profiles


def infer_question_category(question: str, choices: list[str]) -> str:
    text = question.lower()
    if _is_reading_comprehension(text):
        return "reading_comprehension"
    if _contains_any(
        text,
        [
            "theo quy định",
            "pháp luật",
            "bộ luật",
            "luật ",
            "điều ",
            "khoản ",
            "nghị định",
            "xử phạt",
            "hành vi vi phạm",
        ],
    ):
        return "law"
    if _contains_any(
        text,
        [
            "gdp",
            "lạm phát",
            "cung tiền",
            "cầu tiền",
            "kinh tế",
            "tài chính",
            "ngân hàng",
            "chứng khoán",
            "lãi suất",
            "tỷ giá",
            "doanh thu",
            "lợi nhuận",
        ],
    ):
        return "economics_finance"
    if _contains_any(
        text,
        [
            "đạo hàm",
            "tích phân",
            "hàm số",
            "phương trình",
            "bất phương trình",
            "logarit",
            "xác suất",
            "ma trận",
            "hình học",
            "tam giác",
            "sin",
            "cos",
            "√",
            "lim",
        ],
    ) or _looks_formula_heavy(text, choices):
        return "mathematics"
    if _contains_any(
        text,
        [
            "vật lý",
            "gia tốc",
            "điện áp",
            "dòng điện",
            "công suất",
            "tần số",
            "bước sóng",
            "newton",
            "động năng",
            "cơ năng",
            "hóa học",
            "phản ứng",
            "mol",
            "dung dịch",
            "axit",
            "bazơ",
            "este",
            "polyme",
        ],
    ):
        return "science"
    if _contains_any(
        text,
        [
            "thuật toán",
            "cấu trúc dữ liệu",
            "mạng máy tính",
            "cơ sở dữ liệu",
            "hệ điều hành",
            "lập trình",
            "binary",
            "big-o",
            "sql",
            "tcp/ip",
        ],
    ):
        return "computer_science"
    if _contains_any(
        text,
        [
            "năm ",
            "thế kỷ",
            "triều đại",
            "chiến tranh",
            "địa lý",
            "thủ đô",
            "quốc gia",
            "châu lục",
            "biển đông",
            "vĩ độ",
            "kinh độ",
        ],
    ):
        return "history_geography"
    if _contains_any(
        text,
        [
            "đồng nghĩa",
            "trái nghĩa",
            "nghĩa của từ",
            "điền vào chỗ trống",
            "từ nào",
            "phát âm",
            "chính tả",
        ],
    ):
        return "vocabulary_language"
    return "general_knowledge"


def build_public_run_summary(
    *,
    benchmark_path: Path,
    debug_predictions_path: Path,
    public_input_path: Path,
    baseline_submission_path: Path,
    candidate_submission_path: Path,
) -> dict[str, Any]:
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    debug_rows = [json.loads(line) for line in debug_predictions_path.read_text(encoding="utf-8").splitlines() if line]
    latencies = [float(row["latency_ms"]) for row in debug_rows]
    invalid_count = sum(1 for row in debug_rows if row.get("error"))
    fallback_count = sum(1 for row in debug_rows if row.get("used_fallback"))
    disagreement = compute_submission_disagreement(baseline_submission_path, candidate_submission_path)
    profiles = build_question_profile_map(public_input_path)

    changed_by_category: dict[str, int] = {}
    for qid in disagreement["changed_qids"]:
        category = str(profiles.get(qid, {}).get("category", "unknown"))
        changed_by_category[category] = changed_by_category.get(category, 0) + 1

    top_changed_category = None
    top_changed_category_count = 0
    if changed_by_category:
        top_changed_category, top_changed_category_count = max(
            changed_by_category.items(),
            key=lambda item: (item[1], item[0]),
        )

    total_questions = len(debug_rows)
    return {
        "input_file": benchmark["input_file"],
        "output_file": benchmark["output_file"],
        "total_questions": total_questions,
        "average_latency_ms": sum(latencies) / total_questions if total_questions else 0.0,
        "p95_latency_ms": percentile(latencies, 95),
        "invalid_output_rate": invalid_count / total_questions if total_questions else 0.0,
        "fallback_rate": fallback_count / total_questions if total_questions else 0.0,
        "answer_disagreement_count": disagreement["changed_answers"],
        "answer_disagreement_rate": disagreement["disagreement_rate"],
        "top_changed_category": top_changed_category,
        "top_changed_category_count": top_changed_category_count,
        "changed_category_breakdown": changed_by_category,
    }


def _is_reading_comprehension(text: str) -> bool:
    return len(text) >= 700 or _contains_any(
        text,
        [
            "đoạn thông tin",
            "đọc đoạn",
            "theo đoạn văn",
            "theo nội dung được cung cấp",
            "câu hỏi:",
            "[1]",
        ],
    )


def _looks_formula_heavy(text: str, choices: list[str]) -> bool:
    math_signals = sum(text.count(symbol) for symbol in ["=", "+", "-", "*", "/", "^", "∫", "∑"])
    choice_symbols = sum(choice.count(symbol) for choice in choices for symbol in ["=", "+", "-", "/", "^", "√"])
    return math_signals + choice_symbols >= 3


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)
