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


class FullContextRetryProvider(LLMProvider):
    name = "full-context-retry"

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, question: QuestionItem, prompt: str) -> str:
        self.prompts.append(prompt)
        if len(self.prompts) == 1:
            return '{"selected_index": 99}'
        if "khí hậu sa mạc" in prompt and "quân đội Phổ hùng mạnh" in prompt:
            return '{"selected_index": 1}'
        return "thiếu ngữ cảnh đầy đủ"


def test_llm_solver_retry_escalates_to_full_context_for_long_question() -> None:
    provider = FullContextRetryProvider()
    solver = LLMSolver(AppConfig(max_retries=1), provider)
    question = QuestionItem(
        qid="q_long_retry",
        question=(
            "Đoạn thông tin:\n"
            "Đoạn 1: Nội dung không liên quan về khí hậu sa mạc.\n\n"
            "Đoạn 2: Friedrich Wilhelm I được gọi là vua chiến sĩ vì ông xây dựng quân đội Phổ hùng mạnh.\n\n"
            "Đoạn 3: Nội dung khác về thương mại đường biển.\n\n"
            "Câu hỏi: Tại sao Friedrich Wilhelm I được gọi là vua chiến sĩ?"
        ),
        choices=[
            "Vì ông cải cách tài chính",
            "Vì ông xây dựng quân đội Phổ hùng mạnh",
            "Vì ông kết hôn với công chúa Anh",
        ],
    )

    prediction = solver.solve(question)

    assert prediction.used_fallback is False
    assert prediction.selected_index == 1
    assert len(provider.prompts) == 2
