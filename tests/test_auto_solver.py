from app.config import AppConfig
from app.models import QuestionItem
from app.providers.base import LLMProvider
from app.solvers.auto_solver import AutoSolver


class CountingProvider(LLMProvider):
    name = "counting"

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, question: QuestionItem, prompt: str) -> str:
        self.calls += 1
        return '{"selected_index": 0}'


def test_auto_solver_prefers_heuristic_for_deterministic_question() -> None:
    provider = CountingProvider()
    solver = AutoSolver(AppConfig(), provider)
    question = QuestionItem(
        qid="q_gdp",
        question=(
            "Trong một năm nhất định, GDP danh nghĩa của một quốc gia là 500 tỷ USD và GDP thực tế là 400 tỷ USD. "
            "Nếu chỉ số giá GDP của năm trước là 100, thì tỷ lệ lạm phát cho năm hiện tại là bao nhiêu?"
        ),
        choices=["20%", "25%", "30%", "15%"],
    )

    prediction = solver.solve(question)

    assert prediction.selected_index == 1
    assert prediction.provider == "heuristic"
    assert provider.calls == 0
