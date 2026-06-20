import pytest

from app.answer_parser import parse_selected_index


def test_parse_raw_json() -> None:
    assert parse_selected_index('{"selected_index": 2}', 4) == 2


def test_parse_fenced_json() -> None:
    assert parse_selected_index('```json\n{"selected_index": 1}\n```', 4) == 1


def test_parse_json_mixed_with_text() -> None:
    assert parse_selected_index('Result: {"selected_index": 3}', 4) == 3


def test_parse_integer_only_response() -> None:
    assert parse_selected_index("2", 4) == 2


def test_parse_json_with_numeric_string() -> None:
    assert parse_selected_index('{"selected_index": "2"}', 4) == 2


def test_parse_json_with_integer_like_float() -> None:
    assert parse_selected_index('{"selected_index": 2.0}', 4) == 2


def test_parse_json_with_trailing_comma() -> None:
    assert parse_selected_index('{"selected_index": 2,}', 4) == 2


def test_parse_json_with_trailing_comma_and_extra_field() -> None:
    assert parse_selected_index('{"selected_index": 2, "reasoning": "x",}', 4) == 2


def test_parse_truncated_json_missing_closing_brace() -> None:
    assert parse_selected_index('{"selected_index": 2', 4) == 2


def test_parse_embedded_truncated_json_missing_closing_brace() -> None:
    assert parse_selected_index('Kết quả: {"selected_index": 3', 4) == 3


def test_reject_negative_index() -> None:
    with pytest.raises(ValueError):
        parse_selected_index('{"selected_index": -1}', 4)


def test_reject_out_of_range_index() -> None:
    with pytest.raises(ValueError):
        parse_selected_index('{"selected_index": 10}', 4)


def test_reject_empty_response() -> None:
    with pytest.raises(ValueError):
        parse_selected_index("", 4)


def test_reject_invalid_response() -> None:
    with pytest.raises(ValueError):
        parse_selected_index("not valid", 4)


def test_reject_boolean_values() -> None:
    with pytest.raises(ValueError):
        parse_selected_index('{"selected_index": true}', 4)
