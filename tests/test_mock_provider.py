from app.models import QuestionItem
from app.providers.mock_provider import MockProvider


def test_mock_provider_is_deterministic_and_in_range() -> None:
    provider = MockProvider()
    question = QuestionItem(qid="q1", question="Cau hoi", choices=["A", "B", "C"])
    prompt = "prompt"

    first = provider.generate(question, prompt)
    second = provider.generate(question, prompt)

    assert first == second
    assert first.startswith('{"selected_index": ')
