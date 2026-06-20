from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from pydantic import ValidationError

from app.models import QuestionItem

LOGGER = logging.getLogger(__name__)

INPUT_PRIORITY = [
    "/data/private_test.csv",
    "/data/private-test.csv",
    "/data/private_test.json",
    "/data/private-test.json",
    "/data/public_test.csv",
    "/data/public-test.csv",
    "/data/public_test.json",
    "/data/public-test.json",
    "/data/public-test_1780368312.json",
    "/data/public_test_1780368312.json",
    "./data/private_test.csv",
    "./data/private-test.csv",
    "./data/private_test.json",
    "./data/private-test.json",
    "./data/public_test.csv",
    "./data/public-test.csv",
    "./data/public_test.json",
    "./data/public-test.json",
    "./public-test_1780368312.json",
    "./public_test_1780368312.json",
    "./data/sample_public_test.json",
]


def discover_input_file(explicit_path: str | Path | None = None) -> Path:
    if explicit_path is not None:
        candidate = Path(explicit_path)
        if not candidate.exists():
            raise FileNotFoundError(f"Input file not found: {candidate}")
        return candidate

    for candidate in INPUT_PRIORITY:
        path = Path(candidate)
        if path.exists():
            return path
    raise FileNotFoundError("No supported input file found in /data or ./data")


def load_questions(path: Path) -> tuple[list[QuestionItem], int]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        raw_records = json.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".csv":
        raw_records = list(_load_csv_rows(path))
    else:
        raise ValueError(f"Unsupported input format: {path.suffix}")

    questions: list[QuestionItem] = []
    invalid_count = 0

    for index, record in enumerate(raw_records, start=1):
        try:
            questions.append(QuestionItem.model_validate(record))
        except (ValidationError, ValueError, TypeError) as exc:
            invalid_count += 1
            LOGGER.warning("Skipping invalid record %s in %s: %s", index, path, exc)

    return questions, invalid_count


def _load_csv_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = {
                "qid": row.get("qid", ""),
                "question": row.get("question", ""),
                "choices": _extract_choices(row),
            }
            rows.append(normalized)
    return rows


def _extract_choices(row: dict[str, str | None]) -> list[str]:
    choices_raw = row.get("choices")
    if choices_raw:
        parsed = json.loads(choices_raw)
        if not isinstance(parsed, list):
            raise ValueError("choices column must decode to a list")
        return [str(choice) for choice in parsed]

    choice_columns: list[tuple[int, str]] = []
    for key, value in row.items():
        if key is None or not key.startswith("choice_") or value is None or value == "":
            continue
        suffix = key.removeprefix("choice_")
        if suffix.isdigit():
            choice_columns.append((int(suffix), value))

    return [value for _, value in sorted(choice_columns, key=lambda item: item[0])]
