from __future__ import annotations

from dataclasses import replace

from app.config import AppConfig
from app.evaluation.model_benchmark import infer_question_category
from app.main import build_provider
from app.models import Prediction, QuestionItem
from app.providers.base import LLMProvider
from app.solvers.auto_solver import AutoSolver
from app.solvers.base import QuestionSolver
from app.solvers.heuristic_solver import HeuristicSolver
from app.solvers.llm_solver import LLMSolver


class CountingProvider(LLMProvider):
    def __init__(self, wrapped: LLMProvider) -> None:
        self.wrapped = wrapped
        self.name = wrapped.name
        self.call_count = 0

    def ensure_healthy(self) -> None:
        self.wrapped.ensure_healthy()

    def generate(self, question: QuestionItem, prompt: str) -> str:
        self.call_count += 1
        return self.wrapped.generate(question, prompt)

    def reset(self) -> None:
        self.call_count = 0


class SolverHandle:
    def __init__(self, solver: QuestionSolver, provider: CountingProvider | None = None) -> None:
        self.solver = solver
        self.provider = provider

    def solve(self, question: QuestionItem) -> Prediction:
        if self.provider is not None:
            self.provider.reset()
        return self.solver.solve(question)

    @property
    def llm_calls(self) -> int:
        return self.provider.call_count if self.provider is not None else 0


def build_solver_handle(config: AppConfig) -> SolverHandle:
    if config.solver_mode == "heuristic":
        return SolverHandle(HeuristicSolver(config))
    provider = CountingProvider(build_provider(config))
    provider.ensure_healthy()
    if config.solver_mode == "llm":
        return SolverHandle(LLMSolver(config, provider), provider)
    if config.solver_mode == "auto":
        return SolverHandle(AutoSolver(config, provider), provider)
    raise ValueError(f"Unsupported solver mode: {config.solver_mode}")


def resolve_strategy_category(question: QuestionItem) -> str | None:
    if question.category:
        return question.category
    return infer_question_category(question.question, question.choices)


def with_question_category(question: QuestionItem) -> QuestionItem:
    category = resolve_strategy_category(question)
    if category == question.category:
        return question
    return question.model_copy(update={"category": category})


def build_second_pass_config(config: AppConfig, prompt_version: str) -> AppConfig:
    return replace(
        config,
        solver_mode="llm",
        prompt_version=prompt_version,
    )


def resolve_llm_call_count(solver: object, prediction: Prediction) -> int:
    llm_calls = getattr(solver, "llm_calls", None)
    if isinstance(llm_calls, int):
        return llm_calls
    if prediction.provider == "heuristic":
        return 0
    raw_calls = getattr(solver, "calls", None)
    if isinstance(raw_calls, int):
        return raw_calls
    return 0
