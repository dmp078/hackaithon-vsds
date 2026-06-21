from __future__ import annotations

import time

from app.config import AppConfig
from app.models import Prediction, QuestionItem
from app.strategies._helpers import (
    SolverHandle,
    build_second_pass_config,
    build_solver_handle,
    resolve_llm_call_count,
    resolve_strategy_category,
    with_question_category,
)
from app.strategies.base import InferenceStrategy
from app.strategies.models import StrategyExecutionContext, StrategyResult


class RiskSecondPassStrategy(InferenceStrategy):
    name = "risk_second_pass"

    def __init__(
        self,
        config: AppConfig | None = None,
        *,
        first_solver: SolverHandle | None = None,
        second_solver: SolverHandle | None = None,
        risk_threshold: float = 0.75,
        second_pass_prompt_version: str = "compact",
        keep_policy: str = "second",
    ) -> None:
        self.config = config
        self.first_solver = first_solver
        self.second_solver = second_solver
        self.risk_threshold = risk_threshold
        self.second_pass_prompt_version = second_pass_prompt_version
        self.keep_policy = keep_policy

    def execute(
        self,
        question: QuestionItem,
        context: StrategyExecutionContext | None = None,
    ) -> StrategyResult:
        started = time.perf_counter()
        normalized_question = with_question_category(question)
        risk_score, risk_reasons = self._estimate_risk(normalized_question)
        first_solver = self._resolve_first_solver(context)
        first_prediction = first_solver.solve(normalized_question)
        total_llm_calls = resolve_llm_call_count(first_solver, first_prediction)
        intermediate = [first_prediction.model_copy(deep=True)]
        triggered = self._should_trigger(risk_score, first_prediction)
        final_prediction = first_prediction
        kept_answer = "first"

        if triggered:
            second_solver = self._resolve_second_solver(context)
            second_prediction = second_solver.solve(normalized_question)
            total_llm_calls += resolve_llm_call_count(second_solver, second_prediction)
            intermediate.append(second_prediction.model_copy(deep=True))
            final_prediction, kept_answer = self._select_final_prediction(first_prediction, second_prediction)

        final_prediction = final_prediction.model_copy(
            update={"latency_ms": (time.perf_counter() - started) * 1000}
        )
        return StrategyResult(
            final_prediction=final_prediction,
            total_llm_calls=total_llm_calls,
            triggered=triggered,
            metadata={
                "strategy": self.name,
                "question_category": normalized_question.category,
                "risk_score": round(risk_score, 4),
                "risk_reasons": risk_reasons,
                "kept_answer": kept_answer,
                "second_pass_prompt_version": self.second_pass_prompt_version,
                "keep_policy": self.keep_policy,
            },
            intermediate_predictions=intermediate,
        )

    def _should_trigger(self, risk_score: float, first_prediction: Prediction) -> bool:
        if risk_score < self.risk_threshold:
            return False
        if first_prediction.provider == "heuristic":
            return False
        return True

    def _select_final_prediction(self, first_prediction: Prediction, second_prediction: Prediction) -> tuple[Prediction, str]:
        if self.keep_policy == "first":
            return first_prediction, "first"
        if self.keep_policy == "second":
            return second_prediction, "second"
        raise ValueError(f"Unsupported keep policy: {self.keep_policy}")

    def _resolve_first_solver(self, context: StrategyExecutionContext | None) -> SolverHandle:
        if self.first_solver is not None:
            return self.first_solver
        config = self._resolve_config(context)
        self.first_solver = build_solver_handle(config)
        return self.first_solver

    def _resolve_second_solver(self, context: StrategyExecutionContext | None) -> SolverHandle:
        if self.second_solver is not None:
            return self.second_solver
        config = self._resolve_config(context)
        second_config = build_second_pass_config(config, self.second_pass_prompt_version)
        self.second_solver = build_solver_handle(second_config)
        return self.second_solver

    def _resolve_config(self, context: StrategyExecutionContext | None) -> AppConfig:
        if self.config is not None:
            return self.config
        if context is None:
            raise ValueError("StrategyExecutionContext is required when the strategy is built without config")
        return context.config

    def _estimate_risk(self, question: QuestionItem) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []
        category = resolve_strategy_category(question) or "uncategorized"
        question_length = len(question.question)

        if question_length >= 4000:
            score += 0.35
            reasons.append("very_long_passage")
        elif question_length >= 1000:
            score += 0.22
            reasons.append("long_question")
        elif question_length >= 250:
            score += 0.10
            reasons.append("medium_length")

        choice_count = len(question.choices)
        if choice_count >= 10:
            score += 0.24
            reasons.append("many_choices")
        elif choice_count >= 5:
            score += 0.12
            reasons.append("more_than_four_choices")

        category_weights = {
            "reading_comprehension": 0.95,
            "law": 0.80,
            "mathematics": 0.72,
            "science": 0.65,
            "economics_finance": 0.62,
            "history_geography": 0.58,
            "general_knowledge": 0.52,
            "computer_science": 0.50,
            "vocabulary_language": 0.45,
        }
        score += category_weights.get(category, 0.5) * 0.35
        reasons.append(f"category:{category}")

        text = question.question.lower()
        if any(token in text for token in ("theo quy định", "pháp luật", "bộ luật", "điều ", "khoản ", "nghị định")):
            score += 0.18
            reasons.append("legal_wording")
        if any(token in text for token in ("xác suất", "phương trình", "đạo hàm", "tích phân", "ma trận", "biến ngẫu nhiên")):
            score += 0.16
            reasons.append("symbolic_reasoning")
        if any(token in text for token in ("gdp", "lạm phát", "lãi suất", "tỷ giá", "doanh thu", "lợi nhuận", "npv", "irr")):
            score += 0.12
            reasons.append("economics_terms")

        return max(0.0, min(1.0, score)), reasons
