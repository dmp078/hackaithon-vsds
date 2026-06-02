from __future__ import annotations

import hashlib
import json

from app.models import QuestionItem
from app.providers.base import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def generate(self, question: QuestionItem, prompt: str) -> str:
        digest = hashlib.sha256(question.qid.encode("utf-8")).hexdigest()
        selected_index = int(digest[:8], 16) % len(question.choices)
        return json.dumps({"selected_index": selected_index}, ensure_ascii=False)
