from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.config import AppConfig
from app.models import Prediction


@dataclass(slots=True)
class StrategyExecutionContext:
    config: AppConfig


@dataclass(slots=True)
class StrategyResult:
    final_prediction: Prediction
    total_llm_calls: int
    triggered: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    intermediate_predictions: list[Prediction] = field(default_factory=list)
