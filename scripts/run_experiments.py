from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import AppConfig
from app.evaluation.experiments import build_comparison, load_experiment_config, write_comparison_reports
from app.evaluation.runner import run_gold_evaluation
from app.logging_utils import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run configured gold-validation experiments")
    parser.add_argument("--config", type=Path, default=Path("experiments/experiments.yaml"))
    parser.add_argument("--input", type=Path, default=Path("data/gold_validation.json"))
    parser.add_argument("--solver-mode", choices=["llm", "auto", "heuristic"], default="llm")
    parser.add_argument("--provider", choices=["ollama", "mock", "openai-compatible"], default="ollama")
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    experiments = load_experiment_config(args.config)
    summaries = []
    categories_by_experiment = {}

    for experiment in experiments:
        name = str(experiment["name"])
        prompt_version = str(experiment.get("prompt_version", "baseline"))
        config = replace(
            AppConfig.from_env(),
            solver_mode=str(experiment.get("solver_mode", args.solver_mode)),
            provider_name=args.provider,
            prompt_version=prompt_version,
            ollama_model=args.model,
            openai_compatible_model=args.model,
            ollama_num_ctx=int(experiment.get("num_ctx", 16384)),
            ollama_num_predict=int(experiment.get("num_predict", 32)),
            ollama_temperature=float(experiment.get("temperature", 0.0)),
            ollama_think=bool(experiment.get("think", False)),
            retrieval_mode=str(experiment.get("retrieval", "off")),
            retrieval_reranker_mode=str(experiment.get("retrieval_reranker", "off")),
            limit=args.limit,
            log_level=args.log_level,
        )
        print(f"Running experiment: {name}")
        try:
            result = run_gold_evaluation(
                input_path=args.input,
                output_dir=args.reports_dir / name,
                config=config,
                prompt_version=prompt_version,
                experiment_name=name,
            )
        except RuntimeError as exc:
            print(f"Experiment {name} failed: {exc}", file=sys.stderr)
            return 1
        summaries.append(result["summary"])
        categories_by_experiment[name] = result["category_metrics"]

    comparison = build_comparison(summaries, categories_by_experiment)
    write_comparison_reports(args.reports_dir, comparison)
    print(f"Comparison written to: {args.reports_dir / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
