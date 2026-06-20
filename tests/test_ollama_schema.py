from app.providers.ollama_provider import build_selected_index_schema


def test_selected_index_schema_uses_dynamic_maximum() -> None:
    schema = build_selected_index_schema(choice_count=11)

    selected_index = schema["properties"]["selected_index"]
    assert selected_index["type"] == "integer"
    assert selected_index["minimum"] == 0
    assert selected_index["maximum"] == 10
    assert schema["required"] == ["selected_index"]
