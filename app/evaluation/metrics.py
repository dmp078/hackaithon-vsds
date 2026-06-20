from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * (percent / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def build_summary(
    rows: list[dict[str, Any]],
    *,
    experiment_name: str,
    input_file: Path,
    provider: str,
    model: str | None,
    prompt_version: str,
    num_ctx: int,
    num_predict: int,
    temperature: float,
    think: bool,
    total_questions: int | None = None,
) -> dict[str, Any]:
    processed = len(rows)
    correct = sum(1 for row in rows if row["is_correct"])
    invalid_count = sum(1 for row in rows if row.get("error"))
    fallback_count = sum(1 for row in rows if row.get("used_fallback"))
    latencies = [float(row["latency_ms"]) for row in rows]
    return {
        "experiment_name": experiment_name,
        "input_file": str(input_file),
        "total_questions": total_questions if total_questions is not None else processed,
        "processed_questions": processed,
        "correct_predictions": correct,
        "accuracy": correct / processed if processed else 0.0,
        "invalid_output_count": invalid_count,
        "invalid_output_rate": invalid_count / processed if processed else 0.0,
        "fallback_count": fallback_count,
        "fallback_rate": fallback_count / processed if processed else 0.0,
        "average_latency_ms": sum(latencies) / processed if processed else 0.0,
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "max_latency_ms": max(latencies) if latencies else 0.0,
        "provider": provider,
        "model": model,
        "prompt_version": prompt_version,
        "num_ctx": num_ctx,
        "num_predict": num_predict,
        "temperature": temperature,
        "think": think,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_category_metrics(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("category") or "uncategorized"), []).append(row)

    metrics: dict[str, dict[str, float | int]] = {}
    for category, category_rows in sorted(grouped.items()):
        total = len(category_rows)
        correct = sum(1 for row in category_rows if row["is_correct"])
        latencies = [float(row["latency_ms"]) for row in category_rows]
        metrics[category] = {
            "total": total,
            "correct": correct,
            "accuracy": correct / total if total else 0.0,
            "average_latency_ms": sum(latencies) / total if total else 0.0,
        }
    return metrics
