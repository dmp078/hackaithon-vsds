from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import AppConfig
from app.evaluation.model_benchmark import (
    build_public_run_summary,
    build_question_profile_map,
    slugify_model_name,
)
from app.evaluation.runner import run_gold_evaluation
from app.logging_utils import configure_logging
from app.main import run_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark production pipeline across candidate base models")
    parser.add_argument("--gold-input", type=Path, default=Path("data/gold_validation.json"))
    parser.add_argument("--public-input", type=Path, default=Path("public-test_1780368312.json"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports/model_benchmark"))
    parser.add_argument("--submissions-dir", type=Path, default=Path("submissions/model_benchmark"))
    parser.add_argument(
        "--reference-submission",
        type=Path,
        default=Path("submissions/submission_20260620_180431_qwen35_9b_prod_public.csv"),
    )
    parser.add_argument(
        "--baseline-gold-dir",
        type=Path,
        default=Path("reports/final_verification_production"),
    )
    parser.add_argument(
        "--baseline-public-benchmark",
        type=Path,
        default=Path("submissions/benchmark_summary.json"),
    )
    parser.add_argument(
        "--baseline-public-debug",
        type=Path,
        default=Path("submissions/debug_predictions.jsonl"),
    )
    parser.add_argument(
        "--reuse-baseline-artifacts",
        action="store_true",
        help="Reuse verified Qwen baseline artifacts instead of re-running the baseline model",
    )
    parser.add_argument("--provider", choices=["ollama", "openai-compatible"], default="ollama")
    parser.add_argument("--prompt-version", default="baseline")
    parser.add_argument("--baseline-model", default="qwen3.5:9b")
    parser.add_argument("--candidate-model", default="gemma4:e4b")
    parser.add_argument("--log-level", default="WARNING")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)

    models = [args.baseline_model, args.candidate_model]
    base_config = replace(
        AppConfig.from_env(),
        solver_mode="auto",
        provider_name=args.provider,
        prompt_version=args.prompt_version,
        retrieval_mode="off",
        retrieval_reranker_mode="off",
    )

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.submissions_dir.mkdir(parents=True, exist_ok=True)
    public_profiles = build_question_profile_map(args.public_input)

    results: list[dict[str, Any]] = []
    for model_name in models:
        slug = slugify_model_name(model_name)
        model_report_dir = args.reports_dir / slug
        gold_dir = model_report_dir / "gold"
        public_dir = model_report_dir / "public"
        public_dir.mkdir(parents=True, exist_ok=True)

        config = replace(
            base_config,
            ollama_model=model_name,
            openai_compatible_model=model_name,
        )

        if args.reuse_baseline_artifacts and model_name == args.baseline_model:
            gold_result = _load_existing_gold_result(args.baseline_gold_dir)
            submission_path = args.reference_submission
            public_summary = build_public_run_summary(
                benchmark_path=args.baseline_public_benchmark,
                debug_predictions_path=args.baseline_public_debug,
                public_input_path=args.public_input,
                baseline_submission_path=args.reference_submission,
                candidate_submission_path=args.reference_submission,
            )
        else:
            gold_result = run_gold_evaluation(
                input_path=args.gold_input,
                output_dir=gold_dir,
                config=config,
                prompt_version=config.prompt_version,
                experiment_name=f"{slug}_gold",
            )

            submission_path = args.submissions_dir / f"{slug}_public_submission.csv"
            public_config = replace(
                config,
                output_path=submission_path,
                debug_output_path=public_dir / "debug_predictions.jsonl",
                benchmark_output_path=public_dir / "benchmark_summary.json",
            )
            run_batch(
                config=public_config,
                input_path=args.public_input,
                output_path=submission_path,
            )
            public_summary = build_public_run_summary(
                benchmark_path=public_dir / "benchmark_summary.json",
                debug_predictions_path=public_dir / "debug_predictions.jsonl",
                public_input_path=args.public_input,
                baseline_submission_path=args.reference_submission,
                candidate_submission_path=submission_path,
            )
        (public_dir / "summary.json").write_text(
            json.dumps(public_summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        results.append(
            {
                "model": model_name,
                "slug": slug,
                "gold": gold_result["summary"],
                "public": public_summary,
                "gold_rows": gold_result["rows"],
            }
        )

    comparison = build_model_comparison(results, public_profiles)
    (args.reports_dir / "comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.reports_dir / "comparison.md").write_text(
        build_comparison_markdown(comparison),
        encoding="utf-8",
    )
    print(f"Wrote model benchmark reports to {args.reports_dir}")
    return 0


def build_model_comparison(results: list[dict[str, Any]], public_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gold_rows_by_model = {result["model"]: result["gold_rows"] for result in results}
    recommended = sorted(
        results,
        key=lambda result: (
            -float(result["gold"]["accuracy"]),
            float(result["gold"]["average_latency_ms"]),
        ),
    )[0]
    public_question_count = len(public_profiles)
    return {
        "recommended_model": recommended["model"],
        "selection_rule": "highest gold accuracy, then lower average gold latency",
        "public_question_count": public_question_count,
        "models": [
            {
                "model": result["model"],
                "gold": _compact_gold_summary(result["gold"]),
                "public": _compact_public_summary(result["public"]),
            }
            for result in results
        ],
        "gold_pairwise": _build_gold_pairwise_differences(gold_rows_by_model),
    }


def build_comparison_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# Base Model Benchmark",
        "",
        f"- Recommended production candidate: `{comparison['recommended_model']}`",
        f"- Selection rule: {comparison['selection_rule']}",
        f"- Public questions benchmarked: {comparison['public_question_count']}",
        "",
        "## Gold Evaluation",
        "",
        "| Model | Accuracy | Invalid Rate | Fallback Rate | Avg Latency ms | P95 Latency ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_result in comparison["models"]:
        gold = model_result["gold"]
        lines.append(
            f"| {model_result['model']} | {gold['accuracy']:.4f} | {gold['invalid_output_rate']:.4f} | "
            f"{gold['fallback_rate']:.4f} | {gold['average_latency_ms']:.2f} | {gold['p95_latency_ms']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Public Evaluation",
            "",
            "| Model | Avg Latency ms | P95 Latency ms | Invalid Rate | Fallback Rate | Disagreement vs Current Submission | Top Changed Category |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for model_result in comparison["models"]:
        public = model_result["public"]
        lines.append(
            f"| {model_result['model']} | {public['average_latency_ms']:.2f} | {public['p95_latency_ms']:.2f} | "
            f"{public['invalid_output_rate']:.4f} | {public['fallback_rate']:.4f} | "
            f"{public['answer_disagreement_count']} ({public['answer_disagreement_rate']:.4f}) | "
            f"{public['top_changed_category'] or 'n/a'} |"
        )

    pairwise = comparison.get("gold_pairwise", [])
    if pairwise:
        lines.extend(["", "## Gold Pairwise Differences", ""])
        for item in pairwise:
            lines.append(
                f"- `{item['candidate_model']}` vs `{item['reference_model']}`: "
                f"{item['changed_predictions']} changed predictions, "
                f"net_correct_delta={item['net_correct_delta']:+d}. "
                f"Top changed category: {item['top_changed_category'] or 'n/a'}."
            )
    return "\n".join(lines) + "\n"


def _compact_gold_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "accuracy": summary["accuracy"],
        "invalid_output_rate": summary["invalid_output_rate"],
        "fallback_rate": summary["fallback_rate"],
        "average_latency_ms": summary["average_latency_ms"],
        "p95_latency_ms": summary["p95_latency_ms"],
    }


def _compact_public_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "average_latency_ms": summary["average_latency_ms"],
        "p95_latency_ms": summary["p95_latency_ms"],
        "invalid_output_rate": summary["invalid_output_rate"],
        "fallback_rate": summary["fallback_rate"],
        "answer_disagreement_count": summary["answer_disagreement_count"],
        "answer_disagreement_rate": summary["answer_disagreement_rate"],
        "top_changed_category": summary["top_changed_category"],
        "changed_category_breakdown": summary["changed_category_breakdown"],
    }


def _build_gold_pairwise_differences(gold_rows_by_model: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    model_names = list(gold_rows_by_model.keys())
    if len(model_names) < 2:
        return []
    reference_model = model_names[0]
    reference_rows = {row["qid"]: row for row in gold_rows_by_model[reference_model]}
    pairwise: list[dict[str, Any]] = []
    for candidate_model in model_names[1:]:
        changed_predictions = 0
        net_correct_delta = 0
        changed_by_category: dict[str, int] = {}
        for row in gold_rows_by_model[candidate_model]:
            reference = reference_rows[row["qid"]]
            if reference["predicted_index"] == row["predicted_index"]:
                continue
            changed_predictions += 1
            category = str(row.get("category") or "uncategorized")
            changed_by_category[category] = changed_by_category.get(category, 0) + 1
            net_correct_delta += int(bool(row["is_correct"])) - int(bool(reference["is_correct"]))
        top_changed_category = None
        if changed_by_category:
            top_changed_category = max(changed_by_category.items(), key=lambda item: (item[1], item[0]))[0]
        pairwise.append(
            {
                "reference_model": reference_model,
                "candidate_model": candidate_model,
                "changed_predictions": changed_predictions,
                "net_correct_delta": net_correct_delta,
                "top_changed_category": top_changed_category,
                "changed_category_breakdown": changed_by_category,
            }
        )
    return pairwise


def _load_existing_gold_result(output_dir: Path) -> dict[str, Any]:
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in (output_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines() if line]
    category_metrics = json.loads((output_dir / "category_metrics.json").read_text(encoding="utf-8"))
    return {"summary": summary, "rows": rows, "category_metrics": category_metrics}


if __name__ == "__main__":
    raise SystemExit(main())
