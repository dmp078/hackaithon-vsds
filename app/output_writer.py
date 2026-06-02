from __future__ import annotations

import csv
import json
from pathlib import Path

from app.models import BenchmarkSummary, Prediction


def format_answer_value(selected_index: int, answer_format: str, choices: list[str]) -> str:
    if answer_format == "letter":
        return _index_to_letters(selected_index)
    if answer_format == "zero_based_index":
        return str(selected_index)
    if answer_format == "one_based_index":
        return str(selected_index + 1)
    if answer_format == "full_text":
        return choices[selected_index]
    raise ValueError(f"Unsupported answer format: {answer_format}")


def write_outputs(
    predictions: list[Prediction],
    csv_path: Path,
    debug_path: Path,
    benchmark_path: Path,
    answer_format: str,
    summary: BenchmarkSummary,
    question_choices_map: dict[str, list[str]] | None = None,
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    debug_path.parent.mkdir(parents=True, exist_ok=True)
    benchmark_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["qid", "answer"])
        for prediction in predictions:
            answer = prediction.answer or _resolve_answer(
                prediction,
                answer_format,
                question_choices_map,
            )
            prediction.answer = answer
            writer.writerow([prediction.qid, answer])

    with debug_path.open("w", encoding="utf-8") as handle:
        for prediction in predictions:
            handle.write(json.dumps(prediction.model_dump(), ensure_ascii=False) + "\n")

    benchmark_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")


def _resolve_answer(
    prediction: Prediction,
    answer_format: str,
    question_choices_map: dict[str, list[str]] | None,
) -> str:
    if answer_format == "full_text":
        if not question_choices_map or prediction.qid not in question_choices_map:
            raise ValueError("Question choices are required for full_text output")
        return format_answer_value(prediction.selected_index, answer_format, question_choices_map[prediction.qid])
    return format_answer_value(prediction.selected_index, answer_format, [])


def _index_to_letters(index: int) -> str:
    result = ""
    value = index
    while True:
        result = chr(ord("A") + (value % 26)) + result
        value = value // 26 - 1
        if value < 0:
            break
    return result
