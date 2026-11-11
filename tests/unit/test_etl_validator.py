from decimal import Decimal

import pytest
from pydantic import ValidationError

from ai_jobs.etl.validator import SourceVacancy
from tests.unit.etl_helpers import make_source_row


def test_source_vacancy_validates_correct_row():
    vacancy = SourceVacancy.model_validate(make_source_row())

    assert vacancy.source_job_id == "JOB-001"
    assert vacancy.salary_usd == Decimal("100000.00")
    assert vacancy.hiring_difficulty == Decimal("7.4")


def test_empty_certification_becomes_none():
    vacancy = SourceVacancy.model_validate(make_source_row())

    assert vacancy.required_certifications is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("yes", True),
        ("1", True),
        ("false", False),
        ("no", False),
        ("0", False),
    ],
)
def test_boolean_values_are_parsed(value, expected):
    row = make_source_row(Equity_Offered=value)

    vacancy = SourceVacancy.model_validate(row)

    assert vacancy.equity_offered is expected


def test_invalid_boolean_is_rejected():
    row = make_source_row(Equity_Offered="maybe")

    with pytest.raises(ValidationError):
        SourceVacancy.model_validate(row)


def test_salary_min_cannot_exceed_salary_max():
    row = make_source_row(
        Salary_Min="130000",
        Salary_Max="120000",
        Salary_USD="110000",
    )

    with pytest.raises(ValidationError, match="Salary_Min cannot"):
        SourceVacancy.model_validate(row)


def test_salary_must_be_within_min_and_max():
    row = make_source_row(Salary_USD="130000")

    with pytest.raises(ValidationError, match="Salary_USD must be"):
        SourceVacancy.model_validate(row)


def test_application_deadline_cannot_be_before_posted_date():
    row = make_source_row(
        Posted_Date="2026-02-15",
        Application_Deadline="2026-01-15",
    )

    with pytest.raises(ValidationError, match="Application_Deadline"):
        SourceVacancy.model_validate(row)


def test_decimal_fields_preserve_fractional_values():
    vacancy = SourceVacancy.model_validate(make_source_row())

    assert vacancy.bonus_percentage == Decimal("15.5")
    assert vacancy.remote_work_percentage == Decimal("50.5")
    assert vacancy.company_ai_maturity == Decimal("8.1")


def test_rating_outside_allowed_range_is_rejected():
    row = make_source_row(Hiring_Difficulty_1_10="11")

    with pytest.raises(ValidationError):
        SourceVacancy.model_validate(row)


def test_missing_required_field_is_rejected():
    row = make_source_row()
    del row["Company"]

    with pytest.raises(ValidationError):
        SourceVacancy.model_validate(row)
