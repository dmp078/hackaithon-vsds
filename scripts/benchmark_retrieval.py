from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import AppConfig
from app.evaluation.gold import load_gold_questions
from app.evaluation.runner import run_gold_evaluation
from app.logging_utils import configure_logging
from app.retrieval.pipeline import RetrievalPipeline
from app.reranker.factory import build_reranker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark baseline vs retrieval variants")
    parser.add_argument("--input", type=Path, default=Path("data/gold_validation.json"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports/retrieval_framework"))
    parser.add_argument("--provider", choices=["ollama", "mock", "openai-compatible"], default="ollama")
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--prompt-version", default="baseline")
    parser.add_argument("--log-level", default="WARNING")
    return parser.parse_args()


def run_variant(
    *,
    name: str,
    config: AppConfig,
    input_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    result = run_gold_evaluation(
        input_path=input_path,
        output_dir=output_dir,
        config=config,
        prompt_version=config.prompt_version,
        experiment_name=name,
    )
    retrieval_metrics = measure_retrieval_latency(config, input_path) if config.retrieval_mode == "on" else {
        "retrieval_average_latency_ms": 0.0,
        "retrieval_p95_latency_ms": 0.0,
        "retrieval_enabled_questions": 0,
    }
    return {"summary": result["summary"], "retrieval_metrics": retrieval_metrics}


def measure_retrieval_latency(config: AppConfig, input_path: Path) -> dict[str, object]:
    reranker = build_reranker(config)
    if config.retrieval_reranker_mode == "on" and (reranker is None or not reranker.is_available()):
        return {
            "retrieval_average_latency_ms": 0.0,
            "retrieval_p95_latency_ms": 0.0,
            "retrieval_enabled_questions": 0,
            "retrieval_reranker_available": False,
        }
    pipeline = RetrievalPipeline(config, reranker=reranker)
    latencies: list[float] = []
    enabled_count = 0
    for gold in load_gold_questions(input_path):
        started = time.perf_counter()
        result = pipeline.build_snippets(gold.to_question_item())
        elapsed = (time.perf_counter() - started) * 1000
        if result.gate_enabled:
            latencies.append(elapsed)
            enabled_count += 1
    latencies.sort()
    if not latencies:
        return {
            "retrieval_average_latency_ms": 0.0,
            "retrieval_p95_latency_ms": 0.0,
            "retrieval_enabled_questions": 0,
            "retrieval_reranker_available": reranker is not None and reranker.is_available(),
        }
    p95_index = max(0, int((len(latencies) - 1) * 0.95))
    return {
        "retrieval_average_latency_ms": sum(latencies) / len(latencies),
        "retrieval_p95_latency_ms": latencies[p95_index],
        "retrieval_enabled_questions": enabled_count,
        "retrieval_reranker_available": reranker is not None and reranker.is_available(),
    }


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    base_config = replace(
        AppConfig.from_env(),
        solver_mode="auto",
        provider_name=args.provider,
        prompt_version=args.prompt_version,
        ollama_model=args.model,
        openai_compatible_model=args.model,
    )

    variants = [
        ("baseline", replace(base_config, retrieval_mode="off", retrieval_reranker_mode="off")),
        ("retrieval_bge_m3", replace(base_config, retrieval_mode="on", retrieval_reranker_mode="off")),
        ("retrieval_bge_m3_qwen_rerank", replace(base_config, retrieval_mode="on", retrieval_reranker_mode="on")),
    ]

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for name, config in variants:
        variant_dir = args.reports_dir / name
        outcome = run_variant(name=name, config=config, input_path=args.input, output_dir=variant_dir)
        summary = dict(outcome["summary"])
        summary.update(outcome["retrieval_metrics"])
        rows.append(summary)

    accepted_rows: list[dict[str, object]] = []
    for row in rows:
        if row["experiment_name"] == "retrieval_bge_m3_qwen_rerank" and row.get("retrieval_reranker_available") is False:
            continue
        accepted_rows.append(row)

    comparison_md = [
        "# Retrieval Benchmark",
        "",
        "| Variant | Accuracy | Avg Latency ms | P95 Latency ms | Retrieval Avg ms | Retrieval P95 ms | Retrieval Questions | Invalid Rate | Fallback Rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in accepted_rows:
        comparison_md.append(
            f"| {row['experiment_name']} | {row['accuracy']:.4f} | {row['average_latency_ms']:.2f} | "
            f"{row['p95_latency_ms']:.2f} | {row['retrieval_average_latency_ms']:.2f} | "
            f"{row['retrieval_p95_latency_ms']:.2f} | {row['retrieval_enabled_questions']} | "
            f"{row['invalid_output_rate']:.4f} | {row['fallback_rate']:.4f} |"
        )
    (args.reports_dir / "comparison.md").write_text("\n".join(comparison_md) + "\n", encoding="utf-8")
    (args.reports_dir / "summary.json").write_text(json.dumps(accepted_rows, indent=2), encoding="utf-8")
    print(f"Wrote retrieval benchmark reports to {args.reports_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
