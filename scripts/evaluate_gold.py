from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import AppConfig
from app.evaluation.runner import run_gold_evaluation
from app.logging_utils import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the MCQ agent on curated gold validation data")
    parser.add_argument("--input", type=Path, default=Path("data/gold_validation.json"))
    parser.add_argument("--solver-mode", choices=["llm", "auto", "heuristic"], default="llm")
    parser.add_argument("--provider", choices=["ollama", "mock", "openai-compatible"], default="ollama")
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--prompt-version", default="baseline")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--num-predict", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--think", action="store_true")
    parser.add_argument("--retrieval", choices=["off", "on"], default="off")
    parser.add_argument("--retrieval-reranker", choices=["off", "on"], default="off")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    config = replace(
        AppConfig.from_env(),
        solver_mode=args.solver_mode,
        provider_name=args.provider,
        prompt_version=args.prompt_version,
        ollama_model=args.model,
        openai_compatible_model=args.model,
        ollama_num_ctx=args.num_ctx,
        ollama_num_predict=args.num_predict,
        ollama_temperature=args.temperature,
        ollama_think=args.think,
        retrieval_mode=args.retrieval,
        retrieval_reranker_mode=args.retrieval_reranker,
        limit=args.limit,
        log_level=args.log_level,
    )
    try:
        result = run_gold_evaluation(
            input_path=args.input,
            output_dir=args.output_dir,
            config=config,
            prompt_version=args.prompt_version,
            experiment_name=args.output_dir.name,
        )
    except RuntimeError as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 1

    summary = result["summary"]
    print(f"Experiment: {summary['experiment_name']}")
    print(f"Processed: {summary['processed_questions']}")
    print(f"Accuracy: {summary['accuracy']:.4f}")
    print(f"Average latency ms: {summary['average_latency_ms']:.2f}")
    print(f"Invalid outputs: {summary['invalid_output_count']}")
    print(f"Fallbacks: {summary['fallback_count']}")
    print(f"Reports written to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
