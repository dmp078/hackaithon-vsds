from __future__ import annotations

from typing import Any


def build_markdown_report(
    summary: dict[str, Any],
    category_metrics: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
) -> str:
    slowest = sorted(rows, key=lambda row: float(row["latency_ms"]), reverse=True)[:10]
    incorrect = [row for row in rows if not row["is_correct"] or row.get("error") or row.get("used_fallback")]
    incorrect_by_category: dict[str, list[dict[str, Any]]] = {}
    for row in incorrect:
        incorrect_by_category.setdefault(str(row.get("category") or "uncategorized"), []).append(row)

    weakest_categories = [
        category
        for category, metrics in sorted(
            category_metrics.items(),
            key=lambda item: (float(item[1]["accuracy"]), -int(item[1]["total"])),
        )
        if int(metrics["total"]) > 0
    ][:3]

    lines = [
        f"# Evaluation Report: {summary['experiment_name']}",
        "",
        "## Overall Metrics",
        "",
        f"- Accuracy: {summary['accuracy']:.4f}",
        f"- Correct predictions: {summary['correct_predictions']} / {summary['processed_questions']}",
        f"- Invalid outputs: {summary['invalid_output_count']} ({summary['invalid_output_rate']:.4f})",
        f"- Fallbacks: {summary['fallback_count']} ({summary['fallback_rate']:.4f})",
        f"- Average latency: {summary['average_latency_ms']:.2f} ms",
        f"- P50 latency: {summary['p50_latency_ms']:.2f} ms",
        f"- P95 latency: {summary['p95_latency_ms']:.2f} ms",
        f"- Max latency: {summary['max_latency_ms']:.2f} ms",
        "",
        "## Category Accuracy",
        "",
        "| Category | Total | Correct | Accuracy | Avg Latency ms |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for category, metrics in category_metrics.items():
        lines.append(
            f"| {category} | {metrics['total']} | {metrics['correct']} | "
            f"{metrics['accuracy']:.4f} | {metrics['average_latency_ms']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Latency Table",
            "",
            "| Metric | Value ms |",
            "| --- | ---: |",
            f"| Average | {summary['average_latency_ms']:.2f} |",
            f"| P50 | {summary['p50_latency_ms']:.2f} |",
            f"| P95 | {summary['p95_latency_ms']:.2f} |",
            f"| Max | {summary['max_latency_ms']:.2f} |",
            "",
            "## Ten Slowest Questions",
            "",
            "| QID | Category | Latency ms | Correct |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for row in slowest:
        lines.append(f"| {row['qid']} | {row['category']} | {row['latency_ms']:.2f} | {row['is_correct']} |")

    lines.extend(["", "## Incorrect Questions By Category", ""])
    if not incorrect_by_category:
        lines.append("No incorrect, invalid, or fallback records.")
    for category, category_rows in sorted(incorrect_by_category.items()):
        lines.append(f"### {category}")
        lines.append("")
        for row in category_rows:
            lines.append(
                f"- {row['qid']}: gold={row['gold_index']}, "
                f"predicted={row['predicted_index']}, fallback={row['used_fallback']}"
            )
        lines.append("")

    lines.extend(["## Suggested Next Investigation Areas", ""])
    if weakest_categories:
        for category in weakest_categories:
            metrics = category_metrics[category]
            lines.append(
                f"- Investigate `{category}`: accuracy {metrics['accuracy']:.4f} "
                f"over {metrics['total']} question(s)."
            )
    else:
        lines.append("- No category-level weaknesses were measurable in this run.")
    return "\n".join(lines) + "\n"

