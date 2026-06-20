from __future__ import annotations

import csv
import json
from pathlib import Path


REVIEW_COLUMNS = [
    "qid",
    "category",
    "question",
    "choices_json",
    "gold_index",
    "predicted_index",
    "is_correct",
    "human_verified_gold_index",
    "review_note",
]


def export_manual_review_csv(errors_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with errors_path.open(encoding="utf-8") as source, output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as target:
        writer = csv.DictWriter(target, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for line in source:
            if not line.strip():
                continue
            row = json.loads(line)
            writer.writerow(
                {
                    "qid": row.get("qid"),
                    "category": row.get("category"),
                    "question": row.get("question"),
                    "choices_json": json.dumps(row.get("choices", []), ensure_ascii=False),
                    "gold_index": row.get("gold_index"),
                    "predicted_index": row.get("predicted_index"),
                    "is_correct": row.get("is_correct"),
                    "human_verified_gold_index": "",
                    "review_note": "",
                }
            )
