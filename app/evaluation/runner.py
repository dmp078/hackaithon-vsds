from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import AppConfig
from app.evaluation.gold import GoldQuestion, load_gold_questions
from app.evaluation.metrics import build_category_metrics, build_summary
from app.evaluation.reports import build_markdown_report
from app.main import build_solver


def run_gold_evaluation(
    *,
    input_path: Path,
    output_dir: Path,
    config: AppConfig,
    prompt_version: str,
    experiment_name: str,
) -> dict[str, Any]:
    print(
        "WARNING: data/gold_validation.json is validation-only and should receive "
        "a human spot-check before being treated as an official gold set."
    )
    gold_questions = load_gold_questions(input_path)
    total_question_count = len(gold_questions)
    if config.limit is not None:
        gold_questions = gold_questions[: config.limit]

    solver = build_solver(config)
    rows: list[dict[str, Any]] = []
    for gold in gold_questions:
        rows.append(_evaluate_one(gold, solver, config, prompt_version))

    summary = build_summary(
        rows,
        experiment_name=experiment_name,
        input_file=input_path,
        provider=config.provider_name,
        model=_resolve_model_name(config),
        prompt_version=prompt_version,
        num_ctx=config.ollama_num_ctx,
        num_predict=config.ollama_num_predict,
        temperature=config.ollama_temperature,
        think=config.ollama_think,
        total_questions=total_question_count,
    )
    category_metrics = build_category_metrics(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_dir / "predictions.jsonl", rows)
    error_rows = [row for row in rows if not row["is_correct"] or row.get("error") or row.get("used_fallback")]
    _write_jsonl(output_dir / "errors.jsonl", error_rows)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "category_metrics.json").write_text(
        json.dumps(category_metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(
        build_markdown_report(summary, category_metrics, rows),
        encoding="utf-8",
    )
    return {"summary": summary, "category_metrics": category_metrics, "rows": rows}


def _evaluate_one(gold: GoldQuestion, solver: Any, config: AppConfig, prompt_version: str) -> dict[str, Any]:
    question = gold.to_question_item()
    try:
        prediction = solver.solve(question)
        predicted_index = prediction.selected_index
        error = prediction.error
        raw_response = prediction.raw_response
        latency_ms = prediction.latency_ms
        used_fallback = prediction.used_fallback
    except Exception as exc:
        predicted_index = None
        error = str(exc)
        raw_response = None
        latency_ms = 0.0
        used_fallback = False

    return {
        "qid": gold.qid,
        "category": gold.category,
        "question": gold.question,
        "choices": gold.choices,
        "gold_index": gold.gold_index,
        "predicted_index": predicted_index,
        "is_correct": predicted_index == gold.gold_index,
        "latency_ms": latency_ms,
        "raw_response": raw_response,
        "used_fallback": used_fallback,
        "error": error,
        "prompt_version": prompt_version,
        "provider": config.provider_name,
        "model": _resolve_model_name(config),
        "question_char_length": len(gold.question),
    }


def _resolve_model_name(config: AppConfig) -> str | None:
    if config.provider_name == "ollama":
        return config.ollama_model
    if config.provider_name == "openai-compatible":
        return config.openai_compatible_model
    return config.provider_name


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
