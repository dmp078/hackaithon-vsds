from __future__ import annotations

import logging
import time

from app.answer_parser import parse_selected_index
from app.config import AppConfig
from app.models import Prediction, QuestionItem
from app.prompt_builder import build_prompt, build_repair_prompt
from app.providers.base import LLMProvider
from app.solvers.base import QuestionSolver

LOGGER = logging.getLogger(__name__)


class LLMSolver(QuestionSolver):
    def __init__(self, config: AppConfig, provider: LLMProvider) -> None:
        self.config = config
        self.provider = provider

    def solve(self, question: QuestionItem) -> Prediction:
        started = time.perf_counter()
        last_error: str | None = None
        last_response: str | None = None
        base_prompt = build_prompt(question)

        LOGGER.debug("Question %s input length: %s chars", question.qid, len(question.question))
        if len(question.question) > 6000:
            LOGGER.warning("Question %s is unusually long: %s chars", question.qid, len(question.question))

        for attempt in range(self.config.max_retries + 1):
            prompt = (
                base_prompt
                if attempt == 0 or last_response is None
                else build_repair_prompt(last_response, len(question.choices) - 1, base_prompt)
            )
            try:
                last_response = self.provider.generate(question, prompt)
                selected_index = parse_selected_index(last_response, len(question.choices))
                return Prediction(
                    qid=question.qid,
                    selected_index=selected_index,
                    provider=self.provider.name,
                    latency_ms=(time.perf_counter() - started) * 1000,
                    raw_response=last_response,
                )
            except Exception as exc:
                last_error = str(exc)
                LOGGER.warning(
                    "Attempt %s failed for %s via %s: %s",
                    attempt + 1,
                    question.qid,
                    self.provider.name,
                    exc,
                )

        fallback_index = min(max(self.config.fallback_index, 0), len(question.choices) - 1)
        return Prediction(
            qid=question.qid,
            selected_index=fallback_index,
            provider=self.provider.name,
            latency_ms=(time.perf_counter() - started) * 1000,
            raw_response=last_response,
            error=last_error,
            used_fallback=True,
        )
