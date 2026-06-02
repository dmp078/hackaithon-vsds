from __future__ import annotations

from pathlib import Path

from app.models import BenchmarkSummary, Prediction


def build_benchmark_summary(
    *,
    input_file: Path,
    output_file: Path,
    predictions: list[Prediction],
    solver_mode: str,
    provider: str,
    model: str | None,
    invalid_records: int,
) -> BenchmarkSummary:
    total_questions = len(predictions)
    failed_predictions = sum(1 for prediction in predictions if prediction.error is not None)
    fallback_predictions = sum(1 for prediction in predictions if prediction.used_fallback)
    total_latency_ms = sum(prediction.latency_ms for prediction in predictions)
    average_latency_ms = total_latency_ms / total_questions if total_questions else 0.0
    return BenchmarkSummary(
        input_file=str(input_file),
        output_file=str(output_file),
        total_questions=total_questions,
        successful_predictions=total_questions - failed_predictions,
        failed_predictions=failed_predictions,
        fallback_predictions=fallback_predictions,
        total_latency_ms=total_latency_ms,
        average_latency_ms=average_latency_ms,
        solver_mode=solver_mode,
        provider=provider,
        model=model,
        invalid_records=invalid_records,
    )
