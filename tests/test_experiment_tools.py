from __future__ import annotations

import csv
import json
from pathlib import Path

from app.evaluation.experiments import build_comparison, load_experiment_config
from app.evaluation.review import export_manual_review_csv


def test_load_experiment_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "experiments.yaml"
    config_path.write_text(
        """
experiments:
  - name: compact_ctx_8192
    prompt_version: compact
    num_ctx: 8192
    num_predict: 8
    temperature: 0
    think: false
""".strip(),
        encoding="utf-8",
    )

    experiments = load_experiment_config(config_path)

    assert experiments[0]["name"] == "compact_ctx_8192"
    assert experiments[0]["prompt_version"] == "compact"
    assert experiments[0]["num_ctx"] == 8192


def test_build_comparison_prefers_accuracy_then_latency() -> None:
    summaries = [
        {
            "experiment_name": "fast",
            "accuracy": 0.8,
            "average_latency_ms": 100.0,
            "p95_latency_ms": 150.0,
            "invalid_output_rate": 0.0,
            "fallback_rate": 0.0,
        },
        {
            "experiment_name": "accurate",
            "accuracy": 0.9,
            "average_latency_ms": 200.0,
            "p95_latency_ms": 250.0,
            "invalid_output_rate": 0.0,
            "fallback_rate": 0.0,
        },
    ]
    categories = {
        "fast": {"math": {"accuracy": 0.8}, "reading": {"accuracy": 0.7}},
        "accurate": {"math": {"accuracy": 1.0}, "reading": {"accuracy": 0.8}},
    }

    comparison = build_comparison(summaries, categories)

    assert comparison[0]["experiment"] == "accurate"
    assert comparison[0]["best_category"] == "math"
    assert comparison[0]["weakest_category"] == "reading"


def test_export_manual_review_csv(tmp_path: Path) -> None:
    errors_path = tmp_path / "errors.jsonl"
    output_path = tmp_path / "manual_review.csv"
    errors_path.write_text(
        json.dumps(
            {
                "qid": "q1",
                "category": "math",
                "question": "1+1?",
                "choices": ["1", "2"],
                "gold_index": 1,
                "predicted_index": 0,
                "is_correct": False,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    export_manual_review_csv(errors_path, output_path)

    rows = list(csv.DictReader(output_path.open(encoding="utf-8")))
    assert rows[0]["qid"] == "q1"
    assert rows[0]["choices_json"] == '["1", "2"]'
    assert rows[0]["human_verified_gold_index"] == ""
    assert rows[0]["review_note"] == ""
