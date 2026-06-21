from __future__ import annotations

from app.config import AppConfig
from app.models import QuestionItem
from app.strategies._helpers import build_solver_handle, resolve_llm_call_count, with_question_category
from app.strategies.base import InferenceStrategy
from app.strategies.models import StrategyExecutionContext, StrategyResult


class BaselineStrategy(InferenceStrategy):
    name = "baseline"

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config
        self._solver_handle = build_solver_handle(config) if config is not None else None

    def execute(
        self,
        question: QuestionItem,
        context: StrategyExecutionContext | None = None,
    ) -> StrategyResult:
        solver_handle = self._resolve_solver_handle(context)
        normalized_question = with_question_category(question)
        prediction = solver_handle.solve(normalized_question)
        return StrategyResult(
            final_prediction=prediction,
            total_llm_calls=resolve_llm_call_count(solver_handle, prediction),
            triggered=False,
            metadata={"strategy": self.name, "question_category": normalized_question.category},
            intermediate_predictions=[prediction.model_copy(deep=True)],
        )

    def _resolve_solver_handle(self, context: StrategyExecutionContext | None):
        if self._solver_handle is not None:
            return self._solver_handle
        if context is None:
            raise ValueError("StrategyExecutionContext is required when the strategy is built without config")
        self._solver_handle = build_solver_handle(context.config)
        return self._solver_handle
