from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_experiment_config(path: Path) -> list[dict[str, Any]]:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        payload = _parse_simple_experiment_yaml(path.read_text(encoding="utf-8"))
    else:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    experiments = payload.get("experiments", []) if isinstance(payload, dict) else []
    if not isinstance(experiments, list):
        raise ValueError("experiments config must contain an experiments list")
    return [dict(experiment) for experiment in experiments]


def build_comparison(
    summaries: list[dict[str, Any]],
    category_metrics_by_experiment: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for summary in summaries:
        experiment_name = str(summary["experiment_name"])
        category_metrics = category_metrics_by_experiment.get(experiment_name, {})
        rows.append(
            {
                "experiment": experiment_name,
                "accuracy": summary["accuracy"],
                "average_latency_ms": summary["average_latency_ms"],
                "p95_latency_ms": summary["p95_latency_ms"],
                "invalid_output_rate": summary["invalid_output_rate"],
                "fallback_rate": summary["fallback_rate"],
                "best_category": _select_category(category_metrics, best=True),
                "weakest_category": _select_category(category_metrics, best=False),
            }
        )
    return sorted(rows, key=lambda row: (-float(row["accuracy"]), float(row["average_latency_ms"])))


def write_comparison_reports(reports_dir: Path, comparison: list[dict[str, Any]]) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    lines = [
        "# Experiment Comparison",
        "",
        "Sorted by accuracy first, then average latency.",
        "",
        "| Experiment | Accuracy | Avg Latency ms | P95 Latency ms | Invalid Rate | Fallback Rate | Best Category | Weakest Category |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in comparison:
        lines.append(
            f"| {row['experiment']} | {row['accuracy']:.4f} | {row['average_latency_ms']:.2f} | "
            f"{row['p95_latency_ms']:.2f} | {row['invalid_output_rate']:.4f} | "
            f"{row['fallback_rate']:.4f} | {row['best_category']} | {row['weakest_category']} |"
        )
    (reports_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _select_category(category_metrics: dict[str, dict[str, Any]], *, best: bool) -> str | None:
    if not category_metrics:
        return None
    key = (
        (lambda item: (float(item[1].get("accuracy", 0.0)), int(item[1].get("total", 0))))
        if best
        else (lambda item: (float(item[1].get("accuracy", 0.0)), -int(item[1].get("total", 0))))
    )
    return sorted(category_metrics.items(), key=key, reverse=best)[0][0]


def _parse_simple_experiment_yaml(text: str) -> dict[str, list[dict[str, Any]]]:
    experiments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "experiments:":
            continue
        if line.startswith("- "):
            if current is not None:
                experiments.append(current)
            current = {}
            line = line[2:].strip()
            if line:
                key, value = line.split(":", 1)
                current[key.strip()] = _parse_scalar(value.strip())
            continue
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = _parse_scalar(value.strip())
    if current is not None:
        experiments.append(current)
    return {"experiments": experiments}


def _parse_scalar(value: str) -> Any:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"')

