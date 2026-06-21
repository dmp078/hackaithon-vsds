from __future__ import annotations

import csv
import json
from pathlib import Path

from app.evaluation.strategy_benchmark import build_public_strategy_summary, serialize_strategy_result
from app.models import Prediction, QuestionItem
from app.strategies.models import StrategyResult
from app.strategies.registry import build_strategy
from app.strategies.risk_second_pass import RiskSecondPassStrategy
from app.strategies.selective_elimination import SelectiveEliminationStrategy


class _StubSolver:
    def __init__(self, prediction: Prediction) -> None:
        self.prediction = prediction
        self.calls = 0

    def solve(self, question: QuestionItem) -> Prediction:
        self.calls += 1
        return self.prediction.model_copy(deep=True)


def test_registry_builds_known_strategies() -> None:
    baseline = build_strategy("baseline")
    risk = build_strategy("risk_second_pass")
    elimination = build_strategy("selective_elimination")

    assert baseline.name == "baseline"
    assert risk.name == "risk_second_pass"
    assert elimination.name == "selective_elimination"


def test_risk_second_pass_triggers_for_high_risk_question() -> None:
    first_solver = _StubSolver(
        Prediction(qid="q1", selected_index=1, provider="ollama", latency_ms=120.0, raw_response='{"selected_index": 1}')
    )
    second_solver = _StubSolver(
        Prediction(qid="q1", selected_index=2, provider="ollama", latency_ms=140.0, raw_response='{"selected_index": 2}')
    )
    strategy = RiskSecondPassStrategy(
        first_solver=first_solver,
        second_solver=second_solver,
        risk_threshold=0.4,
        keep_policy="second",
    )
    question = QuestionItem(
        qid="q1",
        question="Đoạn thông tin: " + ("A" * 5000),
        choices=["A", "B", "C", "D"],
        category="reading_comprehension",
    )

    result = strategy.execute(question)

    assert result.final_prediction.selected_index == 2
    assert result.total_llm_calls == 2
    assert result.triggered is True
    assert result.metadata["kept_answer"] == "second"
    assert len(result.intermediate_predictions) == 2


def test_risk_second_pass_skips_low_risk_question() -> None:
    first_solver = _StubSolver(
        Prediction(qid="q1", selected_index=0, provider="heuristic", latency_ms=1.0)
    )
    second_solver = _StubSolver(
        Prediction(qid="q1", selected_index=1, provider="ollama", latency_ms=100.0)
    )
    strategy = RiskSecondPassStrategy(
        first_solver=first_solver,
        second_solver=second_solver,
        risk_threshold=0.8,
        keep_policy="second",
    )
    question = QuestionItem(
        qid="q1",
        question="2 + 2 bằng bao nhiêu?",
        choices=["4", "5", "6", "7"],
        category="mathematics",
    )

    result = strategy.execute(question)

    assert result.final_prediction.selected_index == 0
    assert result.total_llm_calls == 0
    assert result.triggered is False
    assert len(result.intermediate_predictions) == 1


def test_selective_elimination_triggers_for_many_choice_question_and_maps_back_to_original_index() -> None:
    baseline_solver = _StubSolver(
        Prediction(qid="q1", selected_index=7, provider="ollama", latency_ms=120.0, raw_response='{"selected_index": 7}')
    )
    elimination_provider = _StubSolver(
        Prediction(
            qid="q1",
            selected_index=0,
            provider="ollama",
            latency_ms=80.0,
            raw_response='{"candidate_indices": [2, 5, 7]}',
        )
    )
    final_solver = _StubSolver(
        Prediction(qid="q1", selected_index=1, provider="ollama", latency_ms=100.0, raw_response='{"selected_index": 1}')
    )
    strategy = SelectiveEliminationStrategy(
        baseline_solver=baseline_solver,
        elimination_provider=elimination_provider,
        final_solver=final_solver,
        min_choice_count=8,
    )
    question = QuestionItem(
        qid="q1",
        question="Theo quy định nào là phương án đúng nhất trong danh sách sau?",
        choices=[f"Phương án {index}" for index in range(10)],
        category="law",
    )

    result = strategy.execute(question)

    assert result.triggered is True
    assert result.total_llm_calls == 3
    assert result.final_prediction.selected_index == 5
    assert result.metadata["candidate_indices"] == [2, 5, 7]
    assert result.metadata["baseline_selected_index"] == 7
    assert len(result.intermediate_predictions) == 3


def test_selective_elimination_skips_low_risk_question_and_returns_baseline_answer() -> None:
    baseline_solver = _StubSolver(
        Prediction(qid="q1", selected_index=1, provider="ollama", latency_ms=120.0, raw_response='{"selected_index": 1}')
    )
    elimination_provider = _StubSolver(
        Prediction(
            qid="q1",
            selected_index=0,
            provider="ollama",
            latency_ms=80.0,
            raw_response='{"candidate_indices": [0, 1]}',
        )
    )
    final_solver = _StubSolver(
        Prediction(qid="q1", selected_index=0, provider="ollama", latency_ms=100.0, raw_response='{"selected_index": 0}')
    )
    strategy = SelectiveEliminationStrategy(
        baseline_solver=baseline_solver,
        elimination_provider=elimination_provider,
        final_solver=final_solver,
        min_choice_count=8,
    )
    question = QuestionItem(
        qid="q1",
        question="2 + 2 bằng bao nhiêu?",
        choices=["1", "4", "6", "8"],
        category="mathematics",
    )

    result = strategy.execute(question)

    assert result.triggered is False
    assert result.total_llm_calls == 1
    assert result.final_prediction.selected_index == 1
    assert len(result.intermediate_predictions) == 1


def test_selective_elimination_does_not_misfire_on_dieu_hanh_phrase_in_technical_question() -> None:
    baseline_solver = _StubSolver(
        Prediction(qid="q1", selected_index=3, provider="ollama", latency_ms=120.0, raw_response='{"selected_index": 3}')
    )
    elimination_provider = _StubSolver(
        Prediction(
            qid="q1",
            selected_index=0,
            provider="ollama",
            latency_ms=80.0,
            raw_response='{"candidate_indices": [0, 1, 2]}',
        )
    )
    final_solver = _StubSolver(
        Prediction(qid="q1", selected_index=0, provider="ollama", latency_ms=100.0, raw_response='{"selected_index": 0}')
    )
    strategy = SelectiveEliminationStrategy(
        baseline_solver=baseline_solver,
        elimination_provider=elimination_provider,
        final_solver=final_solver,
        min_choice_count=8,
    )
    question = QuestionItem(
        qid="q1",
        question="Trong hệ điều hành, cơ chế phân trang bộ nhớ hoạt động như thế nào?",
        choices=[f"Phương án {index}" for index in range(10)],
        category="computer_science",
    )

    result = strategy.execute(question)

    assert result.triggered is False
    assert result.final_prediction.selected_index == 3


def test_public_strategy_summary_aggregates_strategy_metrics(tmp_path: Path) -> None:
    public_input = tmp_path / "public.json"
    public_input.write_text(
        json.dumps(
            [
                {"qid": "q1", "question": "GDP là gì?", "choices": ["A", "B", "C", "D"]},
                {"qid": "q2", "question": "Đoạn thông tin: " + ("B" * 5000), "choices": ["A", "B", "C", "D"]},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    baseline_submission = tmp_path / "baseline.csv"
    with baseline_submission.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["qid", "answer"])
        writer.writerow(["q1", "A"])
        writer.writerow(["q2", "B"])
    candidate_submission = tmp_path / "candidate.csv"
    with candidate_submission.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["qid", "answer"])
        writer.writerow(["q1", "A"])
        writer.writerow(["q2", "C"])

    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(
        json.dumps({"input_file": str(public_input), "output_file": str(candidate_submission)}),
        encoding="utf-8",
    )
    debug_path = tmp_path / "debug.jsonl"
    rows = [
        serialize_strategy_result(
            StrategyResult(
                final_prediction=Prediction(qid="q1", selected_index=0, answer="A", provider="heuristic", latency_ms=1.0),
                total_llm_calls=0,
                triggered=False,
                metadata={"risk_score": 0.1},
                intermediate_predictions=[],
            ),
            question=QuestionItem(qid="q1", question="GDP là gì?", choices=["A", "B", "C", "D"], category="economics_finance"),
        ),
        serialize_strategy_result(
            StrategyResult(
                final_prediction=Prediction(qid="q2", selected_index=2, answer="C", provider="ollama", latency_ms=200.0),
                total_llm_calls=2,
                triggered=True,
                metadata={"risk_score": 0.9},
                intermediate_predictions=[],
            ),
            question=QuestionItem(qid="q2", question="Đoạn thông tin: " + ("B" * 5000), choices=["A", "B", "C", "D"], category="reading_comprehension"),
        ),
    ]
    debug_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

    summary = build_public_strategy_summary(
        benchmark_path=benchmark_path,
        debug_predictions_path=debug_path,
        public_input_path=public_input,
        baseline_submission_path=baseline_submission,
        candidate_submission_path=candidate_submission,
        strategy_name="risk_second_pass",
    )

    assert summary["answer_disagreement_count"] == 1
    assert summary["total_llm_calls"] == 2
    assert summary["trigger_count"] == 1
    assert summary["trigger_rate"] == 0.5
    assert summary["top_changed_category"] == "reading_comprehension"
