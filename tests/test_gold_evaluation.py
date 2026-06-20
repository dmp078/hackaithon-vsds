from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.evaluation.gold import load_gold_questions
from app.evaluation.metrics import build_category_metrics, build_summary, percentile
from app.evaluation.runner import run_gold_evaluation
from app.config import AppConfig


def _write_gold(path: Path) -> None:
    payload = [
        {
            "qid": "q1",
            "question": "Chọn đáp án đúng.",
            "choices": ["Trùng", "Trùng", "Khác"],
            "gold_index": 1,
            "gold_answer": "Trùng",
            "category": "duplicate_text",
            "verification_status": "assistant_curated_high_confidence",
            "recommended_use": "validation_only_until_human_spot_check",
        },
        {
            "qid": "q2",
            "question": "Chọn đáp án đúng.",
            "choices": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
            "gold_index": 10,
            "gold_answer": "K",
            "category": "many_choices",
            "verification_status": "assistant_curated_high_confidence",
            "recommended_use": "validation_only_until_human_spot_check",
        },
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_load_gold_questions_preserves_duplicate_answer_text_and_dynamic_choices(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold_validation.json"
    _write_gold(gold_path)

    questions = load_gold_questions(gold_path)

    assert questions[0].gold_index == 1
    assert questions[0].choices[0] == questions[0].choices[1]
    assert questions[1].gold_index == 10
    assert len(questions[1].choices) == 11


def test_load_gold_questions_rejects_out_of_range_gold_index(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold_validation.json"
    gold_path.write_text(
        json.dumps(
            [
                {
                    "qid": "bad",
                    "question": "Question",
                    "choices": ["A", "B"],
                    "gold_index": 2,
                    "category": "invalid",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="gold_index"):
        load_gold_questions(gold_path)


def test_percentile_and_summary_metrics() -> None:
    rows = [
        {"is_correct": True, "latency_ms": 10.0, "used_fallback": False, "error": None},
        {"is_correct": False, "latency_ms": 20.0, "used_fallback": True, "error": "bad"},
        {"is_correct": True, "latency_ms": 30.0, "used_fallback": False, "error": None},
    ]

    assert percentile([10.0, 20.0, 30.0], 50) == 20.0
    summary = build_summary(
        rows,
        experiment_name="baseline",
        input_file=Path("data/gold_validation.json"),
        provider="mock",
        model="mock",
        prompt_version="baseline",
        num_ctx=16384,
        num_predict=32,
        temperature=0.0,
        think=False,
    )

    assert summary["correct_predictions"] == 2
    assert summary["accuracy"] == pytest.approx(2 / 3)
    assert summary["fallback_count"] == 1
    assert summary["invalid_output_count"] == 1
    assert summary["p50_latency_ms"] == 20.0
    assert summary["p95_latency_ms"] == pytest.approx(29.0)


def test_accuracy_by_category() -> None:
    rows = [
        {"category": "math", "is_correct": True, "latency_ms": 100.0},
        {"category": "math", "is_correct": False, "latency_ms": 300.0},
        {"category": "reading", "is_correct": True, "latency_ms": 500.0},
    ]

    metrics = build_category_metrics(rows)

    assert metrics["math"]["total"] == 2
    assert metrics["math"]["correct"] == 1
    assert metrics["math"]["accuracy"] == 0.5
    assert metrics["math"]["average_latency_ms"] == 200.0


def test_run_gold_evaluation_writes_expected_files_with_mock_provider(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold_validation.json"
    output_dir = tmp_path / "reports" / "mock_baseline"
    _write_gold(gold_path)

    result = run_gold_evaluation(
        input_path=gold_path,
        output_dir=output_dir,
        config=AppConfig(provider_name="mock", solver_mode="llm", prompt_version="baseline"),
        prompt_version="baseline",
        experiment_name="mock_baseline",
    )

    assert result["summary"]["processed_questions"] == 2
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "predictions.jsonl").exists()
    assert (output_dir / "errors.jsonl").exists()
    assert (output_dir / "category_metrics.json").exists()
    assert (output_dir / "report.md").exists()
