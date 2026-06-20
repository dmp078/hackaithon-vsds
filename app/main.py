from __future__ import annotations

import argparse
import logging
from pathlib import Path

from app.benchmark import build_benchmark_summary
from app.config import AppConfig
from app.input_loader import discover_input_file, load_questions
from app.logging_utils import configure_logging
from app.models import BenchmarkSummary, QuestionItem
from app.output_writer import format_answer_value, write_outputs
from app.providers.base import LLMProvider
from app.providers.mock_provider import MockProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_compatible_provider import OpenAICompatibleProvider
from app.solvers.auto_solver import AutoSolver
from app.solvers.base import QuestionSolver
from app.solvers.heuristic_solver import HeuristicSolver
from app.solvers.llm_solver import LLMSolver

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vietnamese MCQ answering agent")
    parser.add_argument("--input", type=str, default=None, help="Input JSON or CSV file")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    parser.add_argument("--solver-mode", type=str, default=None, choices=["heuristic", "llm", "auto"])
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["ollama", "mock", "openai-compatible"],
    )
    parser.add_argument(
        "--answer-format",
        type=str,
        default=None,
        choices=["letter", "zero_based_index", "one_based_index", "full_text"],
    )
    parser.add_argument("--prompt-version", type=str, default=None, help="Prompt version for LLM solver")
    parser.add_argument("--limit", type=int, default=None, help="Limit processed questions")
    parser.add_argument("--log-level", type=str, default=None, help="Logging level")
    return parser.parse_args()


def build_provider(config: AppConfig) -> LLMProvider:
    if config.provider_name == "mock":
        return MockProvider()
    if config.provider_name == "ollama":
        return OllamaProvider(config)
    if config.provider_name == "openai-compatible":
        return OpenAICompatibleProvider(config)
    raise ValueError(f"Unsupported provider: {config.provider_name}")


def build_solver(config: AppConfig) -> QuestionSolver:
    if config.solver_mode == "heuristic":
        return HeuristicSolver(config)
    if config.solver_mode == "llm":
        provider = build_provider(config)
        provider.ensure_healthy()
        return LLMSolver(config, provider)
    if config.solver_mode == "auto":
        provider = build_provider(config)
        provider.ensure_healthy()
        return AutoSolver(config, provider)
    raise ValueError(f"Unsupported solver mode: {config.solver_mode}")


def run_batch(
    *,
    config: AppConfig,
    input_path: Path | None = None,
    output_path: Path | None = None,
) -> BenchmarkSummary:
    source_path = discover_input_file(input_path)
    questions, invalid_count = load_questions(source_path)
    if config.limit is not None:
        questions = questions[: config.limit]

    LOGGER.info("Loaded %s valid question(s) from %s", len(questions), source_path)
    LOGGER.info("Invalid records skipped: %s", invalid_count)

    solver = build_solver(config)
    question_lookup = {question.qid: question for question in questions}
    predictions = []

    for position, question in enumerate(questions, start=1):
        LOGGER.info("Processing %s/%s: %s", position, len(questions), question.qid)
        prediction = solver.solve(question)
        prediction.answer = format_answer_value(
            prediction.selected_index,
            config.answer_format,
            question.choices,
        )
        LOGGER.info("Provider: %s", prediction.provider)
        LOGGER.info("Latency: %.2f ms", prediction.latency_ms)
        LOGGER.info("Selected index: %s", prediction.selected_index)
        LOGGER.info("Answer: %s", prediction.answer)
        LOGGER.info("Used fallback: %s", prediction.used_fallback)
        predictions.append(prediction)

    resolved_output_path = output_path or config.output_path
    summary = build_benchmark_summary(
        input_file=source_path,
        output_file=resolved_output_path,
        predictions=predictions,
        solver_mode=config.solver_mode,
        provider=config.provider_name if config.solver_mode in {"llm", "auto"} else (predictions[0].provider if predictions else config.provider_name),
        model=config.ollama_model if config.solver_mode in {"llm", "auto"} else None,
        invalid_records=invalid_count,
    )
    write_outputs(
        predictions,
        resolved_output_path,
        config.debug_output_path,
        config.benchmark_output_path,
        config.answer_format,
        summary,
        question_choices_map={qid: item.choices for qid, item in question_lookup.items()},
    )

    LOGGER.info("Loaded: %s", summary.total_questions)
    LOGGER.info("Processed: %s", summary.total_questions)
    LOGGER.info("Succeeded: %s", summary.successful_predictions)
    LOGGER.info("Failed: %s", summary.failed_predictions)
    LOGGER.info("Fallback predictions: %s", summary.fallback_predictions)
    LOGGER.info("Total latency: %.2f ms", summary.total_latency_ms)
    LOGGER.info("Average latency: %.2f ms", summary.average_latency_ms)
    LOGGER.info("Official output written to: %s", resolved_output_path)
    LOGGER.info("Debug output written to: %s", config.debug_output_path)
    LOGGER.info("Benchmark written to: %s", config.benchmark_output_path)
    return summary


def main() -> None:
    args = parse_args()
    config = AppConfig.from_env().with_overrides(
        solver_mode=args.solver_mode,
        provider_name=args.provider,
        answer_format=args.answer_format,
        prompt_version=args.prompt_version,
        output_path=Path(args.output) if args.output else None,
        log_level=args.log_level,
        limit=args.limit,
    )
    configure_logging(config.log_level)
    run_batch(
        config=config,
        input_path=Path(args.input) if args.input else None,
        output_path=Path(args.output) if args.output else None,
    )


if __name__ == "__main__":
    main()
