import csv
import json
from pathlib import Path

from app.models import BenchmarkSummary, Prediction
from app.output_writer import format_answer_value, write_outputs


def test_write_exact_csv_header_and_letter_mapping(tmp_path: Path) -> None:
    csv_path = tmp_path / "pred.csv"
    debug_path = tmp_path / "debug.jsonl"
    benchmark_path = tmp_path / "benchmark.json"
    predictions = [
        Prediction(qid="q1", selected_index=0, provider="mock", latency_ms=1.0),
        Prediction(qid="q2", selected_index=10, provider="mock", latency_ms=2.0),
    ]
    summary = BenchmarkSummary(
        input_file="input.json",
        output_file=str(csv_path),
        total_questions=2,
        successful_predictions=2,
        failed_predictions=0,
        fallback_predictions=0,
        total_latency_ms=3.0,
        average_latency_ms=1.5,
        solver_mode="heuristic",
        provider="mock",
        model=None,
    )

    write_outputs(predictions, csv_path, debug_path, benchmark_path, "letter", summary)

    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [["qid", "answer"], ["q1", "A"], ["q2", "K"]]


def test_support_zero_based_one_based_and_full_text_formats() -> None:
    assert format_answer_value(0, "zero_based_index", ["A", "B"]) == "0"
    assert format_answer_value(0, "one_based_index", ["A", "B"]) == "1"
    assert format_answer_value(1, "full_text", ["Giống nhau", "Giống nhau"]) == "Giống nhau"


def test_debug_and_benchmark_files_are_written(tmp_path: Path) -> None:
    csv_path = tmp_path / "pred.csv"
    debug_path = tmp_path / "debug.jsonl"
    benchmark_path = tmp_path / "benchmark.json"
    predictions = [
        Prediction(
            qid="q1",
            selected_index=1,
            provider="mock",
            latency_ms=4.0,
            raw_response='{"selected_index": 1}',
        )
    ]
    summary = BenchmarkSummary(
        input_file="input.json",
        output_file=str(csv_path),
        total_questions=1,
        successful_predictions=1,
        failed_predictions=0,
        fallback_predictions=0,
        total_latency_ms=4.0,
        average_latency_ms=4.0,
        solver_mode="heuristic",
        provider="mock",
        model=None,
    )

    write_outputs(predictions, csv_path, debug_path, benchmark_path, "letter", summary)

    debug_lines = debug_path.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(debug_lines[0])["qid"] == "q1"
    assert json.loads(benchmark_path.read_text(encoding="utf-8"))["total_questions"] == 1
