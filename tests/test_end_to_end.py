import csv
import json
from pathlib import Path

from app.config import AppConfig
from app.main import run_batch


def test_end_to_end_heuristic_pipeline(tmp_path: Path) -> None:
    input_path = Path("data/sample_public_test.json")
    output_path = tmp_path / "pred.csv"
    config = AppConfig(
        solver_mode="heuristic",
        answer_format="letter",
        output_path=output_path,
        debug_output_path=tmp_path / "debug_predictions.jsonl",
        benchmark_output_path=tmp_path / "benchmark_summary.json",
    )

    summary = run_batch(config=config, input_path=input_path, output_path=output_path)

    with output_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    debug_lines = (tmp_path / "debug_predictions.jsonl").read_text(encoding="utf-8").strip().splitlines()
    benchmark = json.loads((tmp_path / "benchmark_summary.json").read_text(encoding="utf-8"))

    assert rows[0] == ["qid", "answer"]
    assert len(rows) == 7
    assert len(debug_lines) == 6
    assert benchmark["total_questions"] == 6
    assert summary.total_questions == 6
    assert [row[0] for row in rows[1:]] == [f"test_{index:04d}" for index in range(1, 7)]
