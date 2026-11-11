from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ai_jobs.schemas.vacancy import VacancyCreate, VacancyUpdate


@pytest.fixture
def valid_vacancy_data():
    return {
        "company_id": 1,
        "country_id": 1,
        "job_title_id": 1,
        "specialization_id": 1,
        "industry_id": 1,
        "employment_type_id": 1,
        "company_size": "Large",
        "education_required": "Master's",
        "experience_level": "Senior",
        "years_of_experience": "5.5",
        "salary_usd": "150000",
        "salary_min": "120000",
        "salary_max": "180000",
        "salary_category": "Upper-Mid",
        "bonus_percentage": "15.5",
        "equity_offered": True,
        "benefits_value_usd": "10000",
        "job_openings": 2,
        "competition_level_applicants": 100,
        "hiring_difficulty": "7.4",
        "work_from_home_available": True,
        "remote_work_percentage": "80",
        "job_satisfaction": "8.5",
        "work_life_balance": "7.2",
        "ai_investment_company_millions": "25",
        "company_ai_maturity": "8.1",
        "job_growth_projection_percentage": "20",
        "automation_risk_percentage": "15",
        "gender_diversity_female_percentage": "40",
        "posted_date": date(2026, 8, 1),
        "application_deadline": date(2026, 9, 1),
        "record_created": date(2026, 8, 1),
        "data_source": "Test dataset",
        "skill_ids": [1, 2, 3],
    }


def test_create_vacancy_with_valid_data(valid_vacancy_data):
    vacancy = VacancyCreate(**valid_vacancy_data)

    assert vacancy.salary_usd == Decimal(150000)
    assert vacancy.hiring_difficulty == Decimal("7.4")
    assert vacancy.skill_ids == [1, 2, 3]


def test_create_vacancy_with_min_salary_greater_than_max(
    valid_vacancy_data,
):
    valid_vacancy_data["salary_min"] = "200000"

    with pytest.raises(ValidationError):
        VacancyCreate(**valid_vacancy_data)


def test_create_vacancy_with_salary_outside_range(valid_vacancy_data):
    valid_vacancy_data["salary_usd"] = "200000"

    with pytest.raises(ValidationError):
        VacancyCreate(**valid_vacancy_data)


def test_create_vacancy_with_invalid_rating(valid_vacancy_data):
    valid_vacancy_data["job_satisfaction"] = "11"

    with pytest.raises(ValidationError):
        VacancyCreate(**valid_vacancy_data)


def test_create_vacancy_with_duplicate_skills(valid_vacancy_data):
    valid_vacancy_data["skill_ids"] = [1, 2, 1]

    with pytest.raises(ValidationError):
        VacancyCreate(**valid_vacancy_data)


def test_create_vacancy_with_nonpositive_skill_id(valid_vacancy_data):
    valid_vacancy_data["skill_ids"] = [1, 0]

    with pytest.raises(ValidationError):
        VacancyCreate(**valid_vacancy_data)


def test_update_vacancy_with_one_field():
    update = VacancyUpdate(salary_usd=Decimal(160000))

    assert update.salary_usd == Decimal(160000)


def test_update_vacancy_with_empty_data():
    with pytest.raises(ValidationError):
        VacancyUpdate()


def test_update_vacancy_with_null_salary():
    with pytest.raises(ValidationError):
        VacancyUpdate(salary_usd=None)


def test_update_vacancy_can_clear_certification():
    update = VacancyUpdate(certification_requirement_id=None)

    assert update.certification_requirement_id is None
