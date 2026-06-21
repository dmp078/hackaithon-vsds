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
from app.evaluation.strategy_benchmark import (
    build_public_strategy_summary,
    run_strategy_gold_evaluation,
    run_strategy_public_evaluation,
)
from app.logging_utils import configure_logging
from app.strategies.registry import STRATEGY_REGISTRY


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark inference strategies with shared gold/public reporting")
    parser.add_argument(
        "--strategy",
        action="append",
        choices=sorted(STRATEGY_REGISTRY.keys()),
        dest="strategies",
        help="Strategy name to benchmark. Repeat to run multiple strategies.",
    )
    parser.add_argument("--gold-input", type=Path, default=Path("data/gold_validation.json"))
    parser.add_argument("--public-input", type=Path, default=Path("public-test_1780368312.json"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports/strategy_lab"))
    parser.add_argument("--submissions-dir", type=Path, default=Path("submissions/strategy_lab"))
    parser.add_argument(
        "--reference-submission",
        type=Path,
        default=Path("submissions/submission_20260620_180431_qwen35_9b_prod_public.csv"),
    )
    parser.add_argument("--provider", choices=["ollama", "openai-compatible"], default="ollama")
    parser.add_argument("--solver-mode", choices=["auto", "llm", "heuristic"], default="auto")
    parser.add_argument("--prompt-version", default="baseline")
    parser.add_argument("--log-level", default="WARNING")
    parser.add_argument("--risk-threshold", type=float, default=0.75)
    parser.add_argument("--second-pass-prompt-version", default="compact")
    parser.add_argument("--keep-policy", choices=["first", "second"], default="second")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)

    strategies = args.strategies or ["baseline", "risk_second_pass"]
    base_config = replace(
        AppConfig.from_env(),
        provider_name=args.provider,
        solver_mode=args.solver_mode,
        prompt_version=args.prompt_version,
        retrieval_mode="off",
        retrieval_reranker_mode="off",
    )

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.submissions_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for strategy_name in strategies:
        strategy_kwargs = build_strategy_kwargs(strategy_name, args)
        strategy_report_dir = args.reports_dir / strategy_name
        gold_dir = strategy_report_dir / "gold"
        public_dir = strategy_report_dir / "public"
        submission_path = args.submissions_dir / f"{strategy_name}_submission.csv"

        gold_result = run_strategy_gold_evaluation(
            input_path=args.gold_input,
            output_dir=gold_dir,
            config=base_config,
            prompt_version=base_config.prompt_version,
            experiment_name=f"{strategy_name}_gold",
            strategy_name=strategy_name,
            strategy_kwargs=strategy_kwargs,
        )
        public_result = run_strategy_public_evaluation(
            input_path=args.public_input,
            output_dir=public_dir,
            submission_path=submission_path,
            config=base_config,
            strategy_name=strategy_name,
            strategy_kwargs=strategy_kwargs,
        )
        public_summary = build_public_strategy_summary(
            benchmark_path=public_result["benchmark_path"],
            debug_predictions_path=public_result["debug_predictions_path"],
            public_input_path=args.public_input,
            baseline_submission_path=args.reference_submission,
            candidate_submission_path=submission_path,
            strategy_name=strategy_name,
        )
        (public_dir / "summary.json").write_text(
            json.dumps(public_summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        results.append(
            {
                "strategy_name": strategy_name,
                "strategy_kwargs": strategy_kwargs,
                "gold": gold_result["summary"],
                "gold_rows": gold_result["rows"],
                "public": public_summary,
                "submission_path": str(submission_path),
            }
        )

    comparison = build_strategy_comparison(results)
    (args.reports_dir / "comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.reports_dir / "comparison.md").write_text(
        build_comparison_markdown(comparison),
        encoding="utf-8",
    )
    print(f"Wrote strategy benchmark reports to {args.reports_dir}")
    return 0


def build_strategy_kwargs(strategy_name: str, args: argparse.Namespace) -> dict[str, Any]:
    if strategy_name != "risk_second_pass":
        return {}
    return {
        "risk_threshold": args.risk_threshold,
        "second_pass_prompt_version": args.second_pass_prompt_version,
        "keep_policy": args.keep_policy,
    }


def build_strategy_comparison(results: list[dict[str, Any]]) -> dict[str, Any]:
    recommended = sorted(
        results,
        key=lambda result: (
            -float(result["gold"]["accuracy"]),
            float(result["public"]["average_latency_ms"]),
        ),
    )[0]
    pairwise = _build_gold_pairwise_differences(results)
    return {
        "recommended_strategy": recommended["strategy_name"],
        "selection_rule": "highest gold accuracy, then lower public average latency",
        "strategies": [
            {
                "strategy_name": result["strategy_name"],
                "strategy_kwargs": result["strategy_kwargs"],
                "gold": _compact_gold_summary(result["gold"]),
                "public": _compact_public_summary(result["public"]),
                "submission_path": result["submission_path"],
            }
            for result in results
        ],
        "gold_pairwise": pairwise,
    }


def build_comparison_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# Inference Strategy Benchmark",
        "",
        f"- Recommended strategy: `{comparison['recommended_strategy']}`",
        f"- Selection rule: {comparison['selection_rule']}",
        "",
        "## Gold Evaluation",
        "",
        "| Strategy | Accuracy | Invalid Rate | Fallback Rate | Avg Latency ms | P95 Latency ms | Total LLM Calls | Trigger Rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in comparison["strategies"]:
        gold = result["gold"]
        lines.append(
            f"| {result['strategy_name']} | {gold['accuracy']:.4f} | {gold['invalid_output_rate']:.4f} | "
            f"{gold['fallback_rate']:.4f} | {gold['average_latency_ms']:.2f} | {gold['p95_latency_ms']:.2f} | "
            f"{gold['total_llm_calls']} | {gold['trigger_rate']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Public Evaluation",
            "",
            "| Strategy | Avg Latency ms | P95 Latency ms | Invalid Rate | Fallback Rate | Total LLM Calls | Trigger Rate | Disagreement vs Production Baseline |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for result in comparison["strategies"]:
        public = result["public"]
        lines.append(
            f"| {result['strategy_name']} | {public['average_latency_ms']:.2f} | {public['p95_latency_ms']:.2f} | "
            f"{public['invalid_output_rate']:.4f} | {public['fallback_rate']:.4f} | {public['total_llm_calls']} | "
            f"{public['trigger_rate']:.4f} | {public['answer_disagreement_count']} ({public['answer_disagreement_rate']:.4f}) |"
        )

    if comparison["gold_pairwise"]:
        lines.extend(["", "## Gold Pairwise Differences", ""])
        for item in comparison["gold_pairwise"]:
            lines.append(
                f"- `{item['candidate_strategy']}` vs `{item['reference_strategy']}`: "
                f"{item['changed_predictions']} changed predictions, "
                f"net_correct_delta={item['net_correct_delta']:+d}."
            )
    return "\n".join(lines) + "\n"


def _compact_gold_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "accuracy": summary["accuracy"],
        "invalid_output_rate": summary["invalid_output_rate"],
        "fallback_rate": summary["fallback_rate"],
        "average_latency_ms": summary["average_latency_ms"],
        "p95_latency_ms": summary["p95_latency_ms"],
        "total_llm_calls": summary["total_llm_calls"],
        "trigger_rate": summary["trigger_rate"],
    }


def _compact_public_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "average_latency_ms": summary["average_latency_ms"],
        "p95_latency_ms": summary["p95_latency_ms"],
        "invalid_output_rate": summary["invalid_output_rate"],
        "fallback_rate": summary["fallback_rate"],
        "total_llm_calls": summary["total_llm_calls"],
        "trigger_rate": summary["trigger_rate"],
        "answer_disagreement_count": summary["answer_disagreement_count"],
        "answer_disagreement_rate": summary["answer_disagreement_rate"],
    }


def _build_gold_pairwise_differences(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(results) < 2:
        return []
    reference = results[0]
    reference_rows = {row["qid"]: row for row in reference["gold_rows"]}
    pairwise: list[dict[str, Any]] = []
    for candidate in results[1:]:
        changed_predictions = 0
        net_correct_delta = 0
        for row in candidate["gold_rows"]:
            baseline_row = reference_rows[row["qid"]]
            if baseline_row["predicted_index"] == row["predicted_index"]:
                continue
            changed_predictions += 1
            net_correct_delta += int(bool(row["is_correct"])) - int(bool(baseline_row["is_correct"]))
        pairwise.append(
            {
                "reference_strategy": reference["strategy_name"],
                "candidate_strategy": candidate["strategy_name"],
                "changed_predictions": changed_predictions,
                "net_correct_delta": net_correct_delta,
            }
        )
    return pairwise


if __name__ == "__main__":
    raise SystemExit(main())
