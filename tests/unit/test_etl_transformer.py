from ai_jobs.etl.transformer import extract_skills, transform_vacancy
from ai_jobs.etl.validator import SourceVacancy
from tests.unit.etl_helpers import make_source_row


def test_extract_skills_splits_and_sorts_names():
    result = extract_skills("Python, SQL, Machine Learning")

    assert result == ["Machine Learning", "Python", "SQL"]


def test_extract_skills_removes_duplicates():
    result = extract_skills("Python, SQL, Python, SQL")

    assert result == ["Python", "SQL"]


def test_extract_skills_removes_extra_spaces_and_empty_items():
    result = extract_skills(" Python , , SQL ,, Machine Learning ")

    assert result == ["Machine Learning", "Python", "SQL"]


def test_extract_skills_returns_empty_list_for_empty_string():
    assert extract_skills("") == []


def test_transform_vacancy_maps_source_fields():
    source = SourceVacancy.model_validate(make_source_row())

    result = transform_vacancy(source)

    assert result["source_job_id"] == "JOB-001"
    assert result["company_size"] == "Large"
    assert result["salary_usd"] == source.salary_usd
    assert result["hiring_difficulty"] == source.hiring_difficulty
    assert result["posted_date"] == source.posted_date
    assert "skills_required" not in result
