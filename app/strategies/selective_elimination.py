from __future__ import annotations

import json
import re
import time
from dataclasses import replace
from typing import Protocol

from app.config import AppConfig
from app.main import build_provider
from app.models import Prediction, QuestionItem
from app.strategies._helpers import (
    CountingProvider,
    build_solver_handle,
    resolve_llm_call_count,
    resolve_strategy_category,
    with_question_category,
)
from app.strategies.base import InferenceStrategy
from app.strategies.models import StrategyExecutionContext, StrategyResult


class _PredictionSolver(Protocol):
    def solve(self, question: QuestionItem) -> Prediction:
        ...


class _PromptOnlySolver:
    def __init__(self, provider: CountingProvider, shortlist_size: int) -> None:
        self.provider = provider
        self.shortlist_size = shortlist_size

    def solve(self, question: QuestionItem) -> Prediction:
        self.provider.reset()
        prompt = _build_elimination_prompt(question, self.shortlist_size)
        raw_response = self.provider.generate(question, prompt)
        return Prediction(
            qid=question.qid,
            selected_index=0,
            provider=self.provider.name,
            latency_ms=0.0,
            raw_response=raw_response,
        )

    @property
    def llm_calls(self) -> int:
        return self.provider.call_count


class SelectiveEliminationStrategy(InferenceStrategy):
    name = "selective_elimination"

    def __init__(
        self,
        config: AppConfig | None = None,
        *,
        baseline_solver: _PredictionSolver | None = None,
        elimination_provider: _PredictionSolver | None = None,
        final_solver: _PredictionSolver | None = None,
        min_choice_count: int = 8,
        shortlist_size: int = 3,
        final_prompt_version: str = "compact",
    ) -> None:
        self.config = config
        self.baseline_solver = baseline_solver
        self.elimination_provider = elimination_provider
        self.final_solver = final_solver
        self.min_choice_count = min_choice_count
        self.shortlist_size = shortlist_size
        self.final_prompt_version = final_prompt_version

    def execute(
        self,
        question: QuestionItem,
        context: StrategyExecutionContext | None = None,
    ) -> StrategyResult:
        started = time.perf_counter()
        normalized_question = with_question_category(question)
        baseline_solver = self._resolve_baseline_solver(context)
        baseline_prediction = baseline_solver.solve(normalized_question)
        total_llm_calls = resolve_llm_call_count(baseline_solver, baseline_prediction)
        intermediate_predictions = [baseline_prediction.model_copy(deep=True)]
        trigger_reasons = self._build_trigger_reasons(normalized_question, baseline_prediction)
        triggered = bool(trigger_reasons)

        metadata = {
            "strategy": self.name,
            "question_category": normalized_question.category,
            "baseline_selected_index": baseline_prediction.selected_index,
            "trigger_reasons": trigger_reasons,
            "final_prompt_version": self.final_prompt_version,
            "shortlist_size": self.shortlist_size,
        }
        if not triggered:
            final_prediction = baseline_prediction.model_copy(
                update={"latency_ms": (time.perf_counter() - started) * 1000}
            )
            metadata["kept_answer"] = "baseline"
            return StrategyResult(
                final_prediction=final_prediction,
                total_llm_calls=total_llm_calls,
                triggered=False,
                metadata=metadata,
                intermediate_predictions=intermediate_predictions,
            )

        elimination_solver = self._resolve_elimination_solver(context)
        elimination_prediction = elimination_solver.solve(normalized_question)
        total_llm_calls += resolve_llm_call_count(elimination_solver, elimination_prediction)
        intermediate_predictions.append(elimination_prediction.model_copy(deep=True))
        candidate_indices = _extract_candidate_indices(
            elimination_prediction.raw_response,
            max_index=len(normalized_question.choices) - 1,
            limit=self.shortlist_size,
        )
        if len(candidate_indices) < 2:
            final_prediction = baseline_prediction.model_copy(
                update={"latency_ms": (time.perf_counter() - started) * 1000}
            )
            metadata["kept_answer"] = "baseline"
            metadata["candidate_indices"] = candidate_indices
            metadata["elimination_failed"] = True
            return StrategyResult(
                final_prediction=final_prediction,
                total_llm_calls=total_llm_calls,
                triggered=True,
                metadata=metadata,
                intermediate_predictions=intermediate_predictions,
            )

        reduced_question = normalized_question.model_copy(
            update={"choices": [normalized_question.choices[index] for index in candidate_indices]}
        )
        final_solver = self._resolve_final_solver(context)
        reduced_prediction = final_solver.solve(reduced_question)
        total_llm_calls += resolve_llm_call_count(final_solver, reduced_prediction)
        mapped_index = candidate_indices[reduced_prediction.selected_index]
        final_prediction = reduced_prediction.model_copy(
            update={
                "qid": normalized_question.qid,
                "selected_index": mapped_index,
                "latency_ms": (time.perf_counter() - started) * 1000,
            }
        )
        intermediate_predictions.append(final_prediction.model_copy(deep=True))
        metadata["candidate_indices"] = candidate_indices
        metadata["kept_answer"] = "elimination_final"
        metadata["answer_changed"] = mapped_index != baseline_prediction.selected_index
        return StrategyResult(
            final_prediction=final_prediction,
            total_llm_calls=total_llm_calls,
            triggered=True,
            metadata=metadata,
            intermediate_predictions=intermediate_predictions,
        )

    def _resolve_config(self, context: StrategyExecutionContext | None) -> AppConfig:
        if self.config is not None:
            return self.config
        if context is None:
            raise ValueError("StrategyExecutionContext is required when the strategy is built without config")
        return context.config

    def _resolve_baseline_solver(self, context: StrategyExecutionContext | None) -> _PredictionSolver:
        if self.baseline_solver is not None:
            return self.baseline_solver
        self.baseline_solver = build_solver_handle(self._resolve_config(context))
        return self.baseline_solver

    def _resolve_elimination_solver(self, context: StrategyExecutionContext | None) -> _PredictionSolver:
        if self.elimination_provider is not None:
            return self.elimination_provider
        provider = CountingProvider(build_provider(self._resolve_config(context)))
        provider.ensure_healthy()
        self.elimination_provider = _PromptOnlySolver(provider, shortlist_size=self.shortlist_size)
        return self.elimination_provider

    def _resolve_final_solver(self, context: StrategyExecutionContext | None) -> _PredictionSolver:
        if self.final_solver is not None:
            return self.final_solver
        final_config = replace(
            self._resolve_config(context),
            solver_mode="llm",
            prompt_version=self.final_prompt_version,
        )
        self.final_solver = build_solver_handle(final_config)
        return self.final_solver

    def _build_trigger_reasons(self, question: QuestionItem, baseline_prediction: Prediction) -> list[str]:
        if baseline_prediction.provider == "heuristic":
            return []

        reasons: list[str] = []
        category = resolve_strategy_category(question) or "uncategorized"
        question_length = len(question.question)
        choice_count = len(question.choices)
        text = question.question.lower()

        factual_categories = {"law", "general_knowledge", "history_geography"}
        if category not in factual_categories:
            return reasons

        if choice_count >= self.min_choice_count:
            reasons.append("many_choices")
        elif choice_count >= 6 and 60 <= question_length <= 600:
            reasons.append("mid_length_many_choice")

        if 80 <= question_length <= 500:
            reasons.append("mid_length_factual")

        if category == "law" and (
            "theo quy định" in text
            or "nghị định" in text
            or re.search(r"\bđiều\s+\d+", text)
            or re.search(r"\bkhoản\s+\d+", text)
            or re.search(r"\bluật\b", text)
        ):
            reasons.append("legal_wording")

        if any(token in text for token in ("thủ đô", "quốc gia", "sự kiện", "khái niệm", "định nghĩa")):
            reasons.append("factual_lookup")

        return reasons


def _build_elimination_prompt(question: QuestionItem, shortlist_size: int) -> str:
    choice_lines = "\n".join(f"[{index}] {choice}" for index, choice in enumerate(question.choices))
    max_index = len(question.choices) - 1
    return (
        "Hãy loại các phương án sai rõ ràng trước khi chốt đáp án.\n"
        f"Giữ lại tối đa {shortlist_size} phương án còn khả năng đúng nhất.\n"
        "Không giải thích.\n"
        "Chỉ trả về một JSON object hợp lệ theo schema:\n"
        '{"candidate_indices": [<integer>, ...]}\n'
        f"Mỗi integer phải nằm trong khoảng từ 0 đến {max_index}.\n"
        "candidate_indices phải là danh sách các phương án còn lại, sắp theo mức độ hợp lý giảm dần.\n\n"
        f"Câu hỏi:\n{question.question}\n\n"
        f"Các phương án:\n{choice_lines}"
    )


def _extract_candidate_indices(raw_response: str | None, *, max_index: int, limit: int) -> list[int]:
    if not raw_response:
        return []

    parsed = _load_json_object(raw_response)
    if isinstance(parsed, dict):
        values = parsed.get("candidate_indices")
        if isinstance(values, list):
            indices = _normalize_candidate_indices(values, max_index=max_index, limit=limit)
            if indices:
                return indices

    match = re.search(r"\[(.*?)\]", raw_response, flags=re.DOTALL)
    if not match:
        return []
    raw_values = re.findall(r"-?\d+", match.group(1))
    return _normalize_candidate_indices(raw_values, max_index=max_index, limit=limit)


def _load_json_object(raw_response: str) -> object | None:
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, flags=re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _normalize_candidate_indices(values: list[object], *, max_index: int, limit: int) -> list[int]:
    normalized: list[int] = []
    seen: set[int] = set()
    for value in values:
        try:
            index = int(str(value).strip())
        except (TypeError, ValueError):
            continue
        if index < 0 or index > max_index or index in seen:
            continue
        normalized.append(index)
        seen.add(index)
        if len(normalized) >= limit:
            break
    return normalized
