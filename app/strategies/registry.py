from __future__ import annotations

from typing import Any

from app.strategies.base import InferenceStrategy
from app.strategies.baseline import BaselineStrategy
from app.strategies.risk_second_pass import RiskSecondPassStrategy


STRATEGY_REGISTRY: dict[str, type[InferenceStrategy]] = {
    BaselineStrategy.name: BaselineStrategy,
    RiskSecondPassStrategy.name: RiskSecondPassStrategy,
}


def build_strategy(name: str, **kwargs: Any) -> InferenceStrategy:
    try:
        strategy_cls = STRATEGY_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown strategy: {name}") from exc
    return strategy_cls(**kwargs)
