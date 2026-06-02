from __future__ import annotations

import json
import re


def parse_selected_index(raw_response: str, choice_count: int) -> int:
    if raw_response is None or not raw_response.strip():
        raise ValueError("Empty response")

    normalized = raw_response.strip()

    direct = _parse_json_candidate(normalized, choice_count)
    if direct is not None:
        return direct

    unfenced = _strip_code_fence(normalized)
    direct = _parse_json_candidate(unfenced, choice_count)
    if direct is not None:
        return direct

    embedded_json = _extract_json_object(unfenced)
    if embedded_json is not None:
        parsed = _parse_json_candidate(embedded_json, choice_count)
        if parsed is not None:
            return parsed

    if re.fullmatch(r"[+-]?\d+", unfenced):
        return _validate_selected_index(int(unfenced), choice_count)

    raise ValueError(f"Unable to parse selected_index from response: {raw_response}")


def _strip_code_fence(value: str) -> str:
    fence_match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return value


def _parse_json_candidate(candidate: str, choice_count: int) -> int | None:
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    selected_index = payload.get("selected_index")
    normalized_index = _coerce_integer_like_value(selected_index)
    if normalized_index is None:
        raise ValueError("selected_index must be an integer")
    return _validate_selected_index(normalized_index, choice_count)


def _extract_json_object(value: str) -> str | None:
    start = value.find("{")
    while start != -1:
        depth = 0
        for index in range(start, len(value)):
            char = value[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return value[start : index + 1]
        start = value.find("{", start + 1)
    return None


def _validate_selected_index(selected_index: int, choice_count: int) -> int:
    if selected_index < 0:
        raise ValueError("selected_index must be non-negative")
    if selected_index >= choice_count:
        raise ValueError("selected_index is out of range")
    return selected_index


def _coerce_integer_like_value(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return None
    if isinstance(value, str):
        normalized = value.strip()
        if re.fullmatch(r"[+-]?\d+", normalized):
            return int(normalized)
    return None
