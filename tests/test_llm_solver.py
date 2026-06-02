from app.config import AppConfig
from app.models import QuestionItem
from app.providers.base import LLMProvider
from app.solvers.llm_solver import LLMSolver


class RepairAwareProvider(LLMProvider):
    name = "repair-aware"

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, question: QuestionItem, prompt: str) -> str:
        self.prompts.append(prompt)
        if len(self.prompts) == 1:
            return '{"selected_index": 99}'
        if "Các phương án" in prompt and "Câu hỏi" in prompt:
            return '{"selected_index": 1}'
        return "không đủ ngữ cảnh"


def test_llm_solver_repair_prompt_keeps_original_context() -> None:
    provider = RepairAwareProvider()
    solver = LLMSolver(AppConfig(max_retries=1), provider)
    question = QuestionItem(
        qid="q_retry",
        question="2 + 2 bằng bao nhiêu?",
        choices=["3", "4", "5"],
    )

    prediction = solver.solve(question)

    assert prediction.used_fallback is False
    assert prediction.selected_index == 1
    assert len(provider.prompts) == 2
