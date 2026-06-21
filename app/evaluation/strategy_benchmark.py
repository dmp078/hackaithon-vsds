from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
from typing import Any

from app.config import AppConfig
from app.evaluation.gold import load_gold_questions
from app.evaluation.metrics import build_category_metrics, build_summary, percentile
from app.evaluation.model_benchmark import compute_submission_disagreement, load_submission_answers
from app.evaluation.reports import build_markdown_report
from app.evaluation.runner import _resolve_model_name
from app.input_loader import load_questions
from app.models import Prediction, QuestionItem
from app.output_writer import format_answer_value
from app.strategies.models import StrategyExecutionContext, StrategyResult
from app.strategies.registry import build_strategy


def serialize_strategy_result(
    result: StrategyResult,
    *,
    question: QuestionItem,
    gold_index: int | None = None,
    strategy_name: str | None = None,
    provider_name: str | None = None,
    model_name: str | None = None,
    prompt_version: str | None = None,
) -> dict[str, Any]:
    prediction = result.final_prediction
    row = {
        "qid": question.qid,
        "category": question.category or "uncategorized",
        "question": question.question,
        "choices": question.choices,
        "question_char_length": len(question.question),
        "choice_count": len(question.choices),
        "gold_index": gold_index,
        "predicted_index": prediction.selected_index,
        "is_correct": prediction.selected_index == gold_index if gold_index is not None else None,
        "answer": prediction.answer,
        "latency_ms": prediction.latency_ms,
        "raw_response": prediction.raw_response,
        "used_fallback": prediction.used_fallback,
        "error": prediction.error,
        "provider": prediction.provider,
        "configured_provider": provider_name,
        "model": model_name,
        "prompt_version": prompt_version,
        "strategy_name": strategy_name or str(result.metadata.get("strategy") or "unknown"),
        "total_llm_calls": result.total_llm_calls,
        "triggered": result.triggered,
        "strategy_metadata": result.metadata,
        "intermediate_predictions": [item.model_dump() for item in result.intermediate_predictions],
    }
    return row


def run_strategy_gold_evaluation(
    *,
    input_path: Path,
    output_dir: Path,
    config: AppConfig,
    prompt_version: str,
    experiment_name: str,
    strategy_name: str,
    strategy_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    print(
        "WARNING: data/gold_validation.json is validation-only and should receive "
        "a human spot-check before being treated as an official gold set."
    )
    gold_questions = load_gold_questions(input_path)
    total_question_count = len(gold_questions)
    if config.limit is not None:
        gold_questions = gold_questions[: config.limit]

    strategy = build_strategy(strategy_name, config=config, **(strategy_kwargs or {}))
    context = StrategyExecutionContext(config=config)
    rows: list[dict[str, Any]] = []
    for gold in gold_questions:
        question = gold.to_question_item()
        normalized = _normalize_question(question)
        try:
            result = strategy.execute(normalized, context)
            row = serialize_strategy_result(
                result,
                question=normalized,
                gold_index=gold.gold_index,
                strategy_name=strategy_name,
                provider_name=config.provider_name,
                model_name=_resolve_model_name(config),
                prompt_version=prompt_version,
            )
        except Exception as exc:
            row = _build_failed_row(
                question=normalized,
                strategy_name=strategy_name,
                prompt_version=prompt_version,
                provider_name=config.provider_name,
                model_name=_resolve_model_name(config),
                gold_index=gold.gold_index,
                error=str(exc),
            )
        rows.append(row)

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
    _augment_strategy_summary(summary, rows, strategy_name)
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
    (output_dir / "metadata.json").write_text(
        json.dumps(
            _build_metadata(
                config,
                strategy_name,
                strategy_kwargs,
                input_path=input_path,
                output_path=output_dir / "predictions.jsonl",
            ),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(
        build_markdown_report(summary, category_metrics, rows),
        encoding="utf-8",
    )
    return {"summary": summary, "category_metrics": category_metrics, "rows": rows}


def run_strategy_public_evaluation(
    *,
    input_path: Path,
    output_dir: Path,
    submission_path: Path,
    config: AppConfig,
    strategy_name: str,
    strategy_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    questions, invalid_count = load_questions(input_path)
    if config.limit is not None:
        questions = questions[: config.limit]

    strategy = build_strategy(strategy_name, config=config, **(strategy_kwargs or {}))
    context = StrategyExecutionContext(config=config)
    rows: list[dict[str, Any]] = []
    predictions: list[Prediction] = []
    for question in questions:
        normalized = _normalize_question(question)
        try:
            result = strategy.execute(normalized, context)
            prediction = result.final_prediction.model_copy(deep=True)
            prediction.answer = format_answer_value(prediction.selected_index, config.answer_format, normalized.choices)
            result = StrategyResult(
                final_prediction=prediction,
                total_llm_calls=result.total_llm_calls,
                triggered=result.triggered,
                metadata=result.metadata,
                intermediate_predictions=result.intermediate_predictions,
            )
            row = serialize_strategy_result(
                result,
                question=normalized,
                strategy_name=strategy_name,
                provider_name=config.provider_name,
                model_name=_resolve_model_name(config),
                prompt_version=config.prompt_version,
            )
            predictions.append(prediction)
        except Exception as exc:
            prediction = Prediction(
                qid=normalized.qid,
                selected_index=config.fallback_index,
                answer=format_answer_value(config.fallback_index, config.answer_format, normalized.choices),
                provider="strategy_error",
                latency_ms=0.0,
                error=str(exc),
                used_fallback=False,
            )
            predictions.append(prediction)
            row = _build_failed_row(
                question=normalized,
                strategy_name=strategy_name,
                prompt_version=config.prompt_version,
                provider_name="strategy_error",
                model_name=_resolve_model_name(config),
                error=str(exc),
                answer=prediction.answer,
                predicted_index=prediction.selected_index,
            )
        rows.append(row)

    benchmark_summary = {
        "input_file": str(input_path),
        "output_file": str(submission_path),
        "total_questions": len(rows),
        "invalid_records": invalid_count,
        "strategy_name": strategy_name,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    submission_path.parent.mkdir(parents=True, exist_ok=True)
    _write_submission(predictions, submission_path)
    _write_jsonl(output_dir / "debug_predictions.jsonl", rows)
    (output_dir / "benchmark_summary.json").write_text(
        json.dumps(benchmark_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "metadata.json").write_text(
        json.dumps(
            _build_metadata(
                config,
                strategy_name,
                strategy_kwargs,
                input_path=input_path,
                output_path=submission_path,
            ),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return {
        "summary": benchmark_summary,
        "rows": rows,
        "submission_path": submission_path,
        "debug_predictions_path": output_dir / "debug_predictions.jsonl",
        "benchmark_path": output_dir / "benchmark_summary.json",
    }


def build_public_strategy_summary(
    *,
    benchmark_path: Path,
    debug_predictions_path: Path,
    public_input_path: Path,
    baseline_submission_path: Path,
    candidate_submission_path: Path,
    strategy_name: str,
) -> dict[str, Any]:
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    debug_rows = [json.loads(line) for line in debug_predictions_path.read_text(encoding="utf-8").splitlines() if line]
    latencies = [float(row["latency_ms"]) for row in debug_rows]
    invalid_count = sum(1 for row in debug_rows if row.get("error"))
    fallback_count = sum(1 for row in debug_rows if row.get("used_fallback"))
    total_llm_calls = sum(int(row.get("total_llm_calls", 0)) for row in debug_rows)
    trigger_count = sum(1 for row in debug_rows if row.get("triggered"))
    disagreement, disagreement_note = _safe_compute_submission_disagreement(
        baseline_submission_path,
        candidate_submission_path,
    )
    changed_by_category = _build_changed_category_breakdown(public_input_path, disagreement["changed_qids"])
    top_changed_category, top_changed_category_count = _resolve_top_changed_category(changed_by_category)

    total_questions = len(debug_rows)
    return {
        "strategy_name": strategy_name,
        "input_file": benchmark["input_file"],
        "output_file": benchmark["output_file"],
        "total_questions": total_questions,
        "average_latency_ms": sum(latencies) / total_questions if total_questions else 0.0,
        "p95_latency_ms": percentile(latencies, 95),
        "invalid_output_count": invalid_count,
        "invalid_output_rate": invalid_count / total_questions if total_questions else 0.0,
        "fallback_count": fallback_count,
        "fallback_rate": fallback_count / total_questions if total_questions else 0.0,
        "total_llm_calls": total_llm_calls,
        "average_llm_calls": total_llm_calls / total_questions if total_questions else 0.0,
        "trigger_count": trigger_count,
        "trigger_rate": trigger_count / total_questions if total_questions else 0.0,
        "answer_disagreement_count": disagreement["changed_answers"],
        "answer_disagreement_rate": disagreement["disagreement_rate"],
        "answer_disagreement_note": disagreement_note,
        "top_changed_category": top_changed_category,
        "top_changed_category_count": top_changed_category_count,
        "changed_category_breakdown": changed_by_category,
    }


def _normalize_question(question: QuestionItem) -> QuestionItem:
    if question.category:
        return question
    from app.strategies._helpers import with_question_category

    return with_question_category(question)


def _build_failed_row(
    *,
    question: QuestionItem,
    strategy_name: str,
    prompt_version: str,
    provider_name: str,
    model_name: str | None,
    error: str,
    gold_index: int | None = None,
    answer: str | None = None,
    predicted_index: int | None = None,
) -> dict[str, Any]:
    return {
        "qid": question.qid,
        "category": question.category or "uncategorized",
        "question": question.question,
        "choices": question.choices,
        "question_char_length": len(question.question),
        "choice_count": len(question.choices),
        "gold_index": gold_index,
        "predicted_index": predicted_index,
        "is_correct": False if gold_index is not None else None,
        "answer": answer,
        "latency_ms": 0.0,
        "raw_response": None,
        "used_fallback": False,
        "error": error,
        "provider": provider_name,
        "model": model_name,
        "prompt_version": prompt_version,
        "strategy_name": strategy_name,
        "total_llm_calls": 0,
        "triggered": False,
        "strategy_metadata": {"strategy": strategy_name, "error": error},
        "intermediate_predictions": [],
    }


def _augment_strategy_summary(summary: dict[str, Any], rows: list[dict[str, Any]], strategy_name: str) -> None:
    total_questions = len(rows)
    total_llm_calls = sum(int(row.get("total_llm_calls", 0)) for row in rows)
    trigger_count = sum(1 for row in rows if row.get("triggered"))
    summary["strategy_name"] = strategy_name
    summary["total_llm_calls"] = total_llm_calls
    summary["average_llm_calls"] = total_llm_calls / total_questions if total_questions else 0.0
    summary["trigger_count"] = trigger_count
    summary["trigger_rate"] = trigger_count / total_questions if total_questions else 0.0


def _build_changed_category_breakdown(public_input_path: Path, changed_qids: list[str]) -> dict[str, int]:
    raw_records = json.loads(public_input_path.read_text(encoding="utf-8"))
    category_by_qid = {
        str(record["qid"]): str(record.get("category") or _normalize_question(QuestionItem.model_validate(record)).category or "unknown")
        for record in raw_records
    }
    changed_by_category: dict[str, int] = {}
    for qid in changed_qids:
        category = category_by_qid.get(qid, "unknown")
        changed_by_category[category] = changed_by_category.get(category, 0) + 1
    return changed_by_category


def _safe_compute_submission_disagreement(
    baseline_submission_path: Path,
    candidate_submission_path: Path,
) -> tuple[dict[str, Any], str | None]:
    try:
        return compute_submission_disagreement(baseline_submission_path, candidate_submission_path), None
    except ValueError:
        baseline = load_submission_answers(baseline_submission_path)
        candidate = load_submission_answers(candidate_submission_path)
        shared_qids = sorted(set(baseline) & set(candidate))
        changed_qids = [qid for qid in shared_qids if baseline[qid] != candidate[qid]]
        total_questions = len(shared_qids)
        return (
            {
                "total_questions": total_questions,
                "changed_answers": len(changed_qids),
                "disagreement_rate": len(changed_qids) / total_questions if total_questions else 0.0,
                "changed_qids": changed_qids,
            },
            "Compared on shared qids only because submission qid sets differ.",
        )


def _resolve_top_changed_category(changed_by_category: dict[str, int]) -> tuple[str | None, int]:
    if not changed_by_category:
        return None, 0
    category, count = max(changed_by_category.items(), key=lambda item: (item[1], item[0]))
    return category, count


def _build_metadata(
    config: AppConfig,
    strategy_name: str,
    strategy_kwargs: dict[str, Any] | None,
    *,
    input_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    return {
        "strategy_name": strategy_name,
        "strategy_kwargs": _json_ready(strategy_kwargs or {}),
        "input_path": str(input_path) if input_path is not None else None,
        "output_path": str(output_path) if output_path is not None else None,
        "config": _json_ready(asdict(config) if is_dataclass(config) else config),
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return _json_ready(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    return value


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_submission(predictions: list[Prediction], path: Path) -> None:
    lines = ["qid,answer"]
    for prediction in predictions:
        lines.append(f"{prediction.qid},{prediction.answer}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
