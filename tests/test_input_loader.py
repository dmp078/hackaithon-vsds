from pathlib import Path

from app.input_loader import load_questions


def test_load_json_array(tmp_path: Path) -> None:
    path = tmp_path / "sample.json"
    path.write_text(
        '[{"qid":"q1","question":"Thu do?","choices":["Ha Noi","Hue"]}]',
        encoding="utf-8",
    )

    questions, invalid_count = load_questions(path)

    assert invalid_count == 0
    assert len(questions) == 1
    assert questions[0].qid == "q1"


def test_load_csv_with_json_choices_column(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text(
        'qid,question,choices\nq1,"Cau hoi","[""Lua chon 1"",""Lua chon 2""]"\n',
        encoding="utf-8",
    )

    questions, invalid_count = load_questions(path)

    assert invalid_count == 0
    assert questions[0].choices == ["Lua chon 1", "Lua chon 2"]


def test_load_csv_with_dynamic_choice_columns(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text(
        "qid,question,choice_0,choice_1,choice_2\nq1,Cau hoi,A,B,C\n",
        encoding="utf-8",
    )

    questions, invalid_count = load_questions(path)

    assert invalid_count == 0
    assert questions[0].choices == ["A", "B", "C"]


def test_reject_records_with_fewer_than_two_choices(tmp_path: Path) -> None:
    path = tmp_path / "sample.json"
    path.write_text(
        '[{"qid":"q1","question":"Cau hoi","choices":["Only one"]}]',
        encoding="utf-8",
    )

    questions, invalid_count = load_questions(path)

    assert questions == []
    assert invalid_count == 1


def test_preserve_duplicate_choices_and_vietnamese_unicode(tmp_path: Path) -> None:
    path = tmp_path / "sample.json"
    path.write_text(
        '[{"qid":"q1","question":"Thủ đô là gì?","choices":["Giống nhau","Khác","Giống nhau"]}]',
        encoding="utf-8",
    )

    questions, invalid_count = load_questions(path)

    assert invalid_count == 0
    assert questions[0].question == "Thủ đô là gì?"
    assert questions[0].choices == ["Giống nhau", "Khác", "Giống nhau"]
