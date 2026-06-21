from __future__ import annotations

import csv
import json
from pathlib import Path

from app.evaluation.model_benchmark import (
    build_public_run_summary,
    build_question_profile_map,
    compute_submission_disagreement,
    infer_question_category,
)


def _write_submission(path: Path, rows: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["qid", "answer"])
        writer.writerows(rows)


def test_compute_submission_disagreement_counts_changed_answers(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    _write_submission(baseline, [("q1", "A"), ("q2", "B"), ("q3", "C")])
    _write_submission(candidate, [("q1", "A"), ("q2", "D"), ("q3", "B")])

    disagreement = compute_submission_disagreement(baseline, candidate)

    assert disagreement["total_questions"] == 3
    assert disagreement["changed_answers"] == 2
    assert disagreement["disagreement_rate"] == 2 / 3
    assert disagreement["changed_qids"] == ["q2", "q3"]


def test_build_public_run_summary_uses_debug_latencies_and_question_profiles(tmp_path: Path) -> None:
    benchmark_path = tmp_path / "benchmark_summary.json"
    debug_path = tmp_path / "debug_predictions.jsonl"
    public_input_path = tmp_path / "public.json"
    baseline_submission_path = tmp_path / "baseline.csv"
    candidate_submission_path = tmp_path / "candidate.csv"

    benchmark_path.write_text(
        json.dumps(
            {
                "input_file": "public.json",
                "output_file": "candidate.csv",
                "total_questions": 3,
                "successful_predictions": 3,
                "failed_predictions": 0,
                "fallback_predictions": 1,
                "total_latency_ms": 600.0,
                "average_latency_ms": 200.0,
                "solver_mode": "auto",
                "provider": "ollama",
                "model": "gemma3:12b",
                "invalid_records": 0,
            }
        ),
        encoding="utf-8",
    )
    debug_rows = [
        {
            "qid": "q1",
            "selected_index": 0,
            "answer": "A",
            "provider": "ollama",
            "latency_ms": 100.0,
            "raw_response": "{\"selected_index\": 0}",
            "error": None,
            "used_fallback": False,
        },
        {
            "qid": "q2",
            "selected_index": 1,
            "answer": "B",
            "provider": "ollama",
            "latency_ms": 200.0,
            "raw_response": "{\"selected_index\": 1}",
            "error": "invalid",
            "used_fallback": True,
        },
        {
            "qid": "q3",
            "selected_index": 2,
            "answer": "C",
            "provider": "ollama",
            "latency_ms": 300.0,
            "raw_response": "{\"selected_index\": 2}",
            "error": None,
            "used_fallback": False,
        },
    ]
    with debug_path.open("w", encoding="utf-8") as handle:
        for row in debug_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    public_input_path.write_text(
        json.dumps(
            [
                {"qid": "q1", "question": "Theo quy định của pháp luật, điều nào đúng?", "choices": ["A", "B", "C"]},
                {"qid": "q2", "question": "Đoạn thông tin: ... Câu hỏi: nội dung nào đúng?", "choices": ["A", "B"]},
                {"qid": "q3", "question": "Tính đạo hàm của hàm số y = x^2", "choices": ["x", "2x", "x^2"]},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _write_submission(baseline_submission_path, [("q1", "A"), ("q2", "A"), ("q3", "C")])
    _write_submission(candidate_submission_path, [("q1", "A"), ("q2", "B"), ("q3", "B")])

    summary = build_public_run_summary(
        benchmark_path=benchmark_path,
        debug_predictions_path=debug_path,
        public_input_path=public_input_path,
        baseline_submission_path=baseline_submission_path,
        candidate_submission_path=candidate_submission_path,
    )

    assert summary["average_latency_ms"] == 200.0
    assert summary["p95_latency_ms"] == 290.0
    assert summary["invalid_output_rate"] == 1 / 3
    assert summary["fallback_rate"] == 1 / 3
    assert summary["answer_disagreement_count"] == 2
    assert summary["answer_disagreement_rate"] == 2 / 3
    assert summary["top_changed_category"] == "reading_comprehension"


def test_infer_question_category_prioritizes_reading_passages() -> None:
    category = infer_question_category(
        "Đoạn thông tin: Một bài viết dài nhiều đoạn.\n[1] ...\nCâu hỏi: Theo đoạn văn, nhận định nào đúng?",
        ["A", "B", "C", "D"],
    )

    assert category == "reading_comprehension"


def test_build_question_profile_map_collects_category_length_and_choice_count(tmp_path: Path) -> None:
    public_input_path = tmp_path / "public.json"
    public_input_path.write_text(
        json.dumps(
            [
                {"qid": "q1", "question": "GDP là gì?", "choices": ["A", "B", "C", "D"]},
                {"qid": "q2", "question": "Tính tích phân của x", "choices": ["A", "B", "C"]},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    profiles = build_question_profile_map(public_input_path)

    assert profiles["q1"]["choice_count"] == 4
    assert profiles["q1"]["category"] == "economics_finance"
    assert profiles["q2"]["category"] == "mathematics"
