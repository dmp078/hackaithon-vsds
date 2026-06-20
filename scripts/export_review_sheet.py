from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.evaluation.review import export_manual_review_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export manual review CSV from evaluation errors")
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    experiment_dir = args.reports_dir / args.experiment
    errors_path = experiment_dir / "errors.jsonl"
    output_path = experiment_dir / "manual_review.csv"
    export_manual_review_csv(errors_path, output_path)
    print(f"Manual review CSV written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
