from __future__ import annotations

from app.config import AppConfig
from app.models import Prediction, QuestionItem
from app.providers.base import LLMProvider
from app.solvers.base import QuestionSolver
from app.solvers.heuristic_solver import HeuristicSolver
from app.solvers.llm_solver import LLMSolver


class AutoSolver(QuestionSolver):
    def __init__(self, config: AppConfig, provider: LLMProvider) -> None:
        self.heuristic_solver = HeuristicSolver(config)
        self.llm_solver = LLMSolver(config, provider)

    def solve(self, question: QuestionItem) -> Prediction:
        selected_index = self.heuristic_solver.try_solve_confidently(question)
        if selected_index is not None:
            return self.heuristic_solver.solve(question)
        return self.llm_solver.solve(question)
