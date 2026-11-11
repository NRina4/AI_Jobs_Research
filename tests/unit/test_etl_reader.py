import pytest

from ai_jobs.etl.reader import read_csv


def test_read_csv_returns_rows_with_line_numbers(tmp_path):
    source = tmp_path / "jobs.csv"
    source.write_text(
        "Job_ID,Company\n1,OpenAI\n2,Google\n",
        encoding="utf-8",
    )

    rows = list(read_csv(source))

    assert len(rows) == 2
    assert rows[0] == (2, {"Job_ID": "1", "Company": "OpenAI"})
    assert rows[1] == (3, {"Job_ID": "2", "Company": "Google"})


def test_read_csv_supports_utf8_bom(tmp_path):
    source = tmp_path / "jobs.csv"
    source.write_text(
        "\ufeffJob_ID,Company\n1,OpenAI\n",
        encoding="utf-8",
    )

    rows = list(read_csv(source))

    assert rows[0][1]["Job_ID"] == "1"


def test_read_csv_raises_error_for_missing_file(tmp_path):
    source = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        list(read_csv(source))


def test_read_csv_raises_error_for_directory(tmp_path):
    with pytest.raises(ValueError, match="CSV source is not a file"):
        list(read_csv(tmp_path))


def test_read_csv_raises_error_for_empty_file(tmp_path):
    source = tmp_path / "empty.csv"
    source.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file has no header"):
        list(read_csv(source))


def test_read_csv_raises_error_for_extra_values(tmp_path):
    source = tmp_path / "jobs.csv"
    source.write_text(
        "Job_ID,Company\n1,OpenAI,Extra\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="more values than the header"):
        list(read_csv(source))
