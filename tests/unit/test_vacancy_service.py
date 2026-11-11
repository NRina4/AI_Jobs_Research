from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from ai_jobs.models import (
    Company,
    Continent,
    Country,
    EmploymentType,
    Industry,
    JobTitle,
    Skill,
    Specialization,
    Vacancy,
    VacancySkill,
)
from ai_jobs.schemas.vacancy import VacancyCreate, VacancyUpdate
from ai_jobs.services.exceptions import ReferenceNotFoundError
from ai_jobs.services.vacancy import (
    create_vacancy,
    delete_vacancy,
    get_vacancies,
    get_vacancy,
    update_vacancy,
)


@pytest.fixture
def reference_ids(db_session):
    """Create reference records required for a vacancy."""

    continent = Continent(name="Europe")
    db_session.add(continent)
    db_session.flush()

    country = Country(name="Poland", continent_id=continent.id)
    company = Company(name="Test Company")
    job_title = JobTitle(name="AI Engineer")
    specialization = Specialization(name="Machine Learning")
    industry = Industry(name="Technology")
    employment_type = EmploymentType(name="Full-time")
    python_skill = Skill(name="Python")
    sql_skill = Skill(name="SQL")

    db_session.add_all(
        [
            country,
            company,
            job_title,
            specialization,
            industry,
            employment_type,
            python_skill,
            sql_skill,
        ]
    )
    db_session.flush()

    return {
        "company_id": company.id,
        "country_id": country.id,
        "job_title_id": job_title.id,
        "specialization_id": specialization.id,
        "industry_id": industry.id,
        "employment_type_id": employment_type.id,
        "python_skill_id": python_skill.id,
        "sql_skill_id": sql_skill.id,
    }


def make_vacancy_data(reference_ids, **overrides):
    """Build valid vacancy data for service tests."""

    data = {
        "company_id": reference_ids["company_id"],
        "country_id": reference_ids["country_id"],
        "job_title_id": reference_ids["job_title_id"],
        "specialization_id": reference_ids["specialization_id"],
        "industry_id": reference_ids["industry_id"],
        "employment_type_id": reference_ids["employment_type_id"],
        "company_size": "Medium",
        "education_required": "Bachelor's",
        "experience_level": "Mid",
        "years_of_experience": Decimal("3.00"),
        "salary_usd": Decimal("100000.00"),
        "salary_min": Decimal("80000.00"),
        "salary_max": Decimal("120000.00"),
        "salary_category": "Mid",
        "bonus_percentage": Decimal("10.00"),
        "equity_offered": False,
        "benefits_value_usd": Decimal("5000.00"),
        "job_openings": 2,
        "competition_level_applicants": 100,
        "hiring_difficulty": Decimal("5.50"),
        "work_from_home_available": True,
        "remote_work_percentage": Decimal("80.00"),
        "job_satisfaction": Decimal("8.20"),
        "work_life_balance": Decimal("7.50"),
        "ai_investment_company_millions": Decimal("2.50"),
        "company_ai_maturity": Decimal("7.80"),
        "job_growth_projection_percentage": Decimal("15.00"),
        "automation_risk_percentage": Decimal("20.00"),
        "gender_diversity_female_percentage": Decimal("40.00"),
        "posted_date": date(2026, 8, 1),
        "application_deadline": date(2026, 9, 1),
        "record_created": date(2026, 8, 1),
        "data_source": "Unit test",
        "skill_ids": [
            reference_ids["python_skill_id"],
            reference_ids["sql_skill_id"],
        ],
    }

    data.update(overrides)
    return VacancyCreate(**data)


def test_create_vacancy_with_skills(db_session, reference_ids):
    vacancy_data = make_vacancy_data(reference_ids)

    vacancy = create_vacancy(db_session, vacancy_data)

    assert vacancy.id is not None
    assert vacancy.source_job_id.startswith("manual-")
    assert len(vacancy.source_job_id) == 39

    linked_skills = (
        db_session.query(VacancySkill).filter_by(vacancy_id=vacancy.id).all()
    )

    assert len(linked_skills) == 2
    assert {item.skill_id for item in linked_skills} == {
        reference_ids["python_skill_id"],
        reference_ids["sql_skill_id"],
    }


def test_create_vacancy_with_provided_source_job_id(
    db_session,
    reference_ids,
):
    vacancy_data = make_vacancy_data(
        reference_ids,
        source_job_id="external-123",
    )

    vacancy = create_vacancy(db_session, vacancy_data)

    assert vacancy.source_job_id == "external-123"


def test_create_vacancy_with_missing_reference(
    db_session,
    reference_ids,
):
    vacancy_data = make_vacancy_data(
        reference_ids,
        company_id=99999,
    )

    with pytest.raises(ReferenceNotFoundError) as error:
        create_vacancy(db_session, vacancy_data)

    assert error.value.field_name == "company_id"
    assert error.value.object_id == 99999
    assert db_session.query(Vacancy).count() == 0


def test_create_vacancy_with_missing_skill(
    db_session,
    reference_ids,
):
    vacancy_data = make_vacancy_data(
        reference_ids,
        skill_ids=[99999],
    )

    with pytest.raises(ReferenceNotFoundError) as error:
        create_vacancy(db_session, vacancy_data)

    assert error.value.field_name == "skill_id"
    assert error.value.object_id == 99999
    assert db_session.query(Vacancy).count() == 0


def test_get_vacancy_by_id(db_session, reference_ids):
    vacancy_data = make_vacancy_data(reference_ids)
    created_vacancy = create_vacancy(db_session, vacancy_data)

    vacancy = get_vacancy(db_session, created_vacancy.id)

    assert vacancy is not None
    assert vacancy.id == created_vacancy.id


def test_get_nonexistent_vacancy(db_session):
    vacancy = get_vacancy(db_session, 99999)

    assert vacancy is None


def test_get_vacancies_with_pagination(db_session, reference_ids):
    for _ in range(5):
        vacancy_data = make_vacancy_data(
            reference_ids,
            skill_ids=[],
        )
        create_vacancy(db_session, vacancy_data)

    vacancies = get_vacancies(db_session, offset=1, limit=2)

    assert len(vacancies) == 2
    assert vacancies[0].id < vacancies[1].id


def test_update_vacancy(db_session, reference_ids):
    vacancy = create_vacancy(
        db_session,
        make_vacancy_data(reference_ids),
    )

    update_data = VacancyUpdate(
        salary_usd=Decimal("110000.00"),
    )

    updated_vacancy = update_vacancy(
        db_session,
        vacancy.id,
        update_data,
    )

    assert updated_vacancy is not None
    assert updated_vacancy.salary_usd == Decimal("110000.00")
    assert updated_vacancy.salary_min == Decimal("80000.00")


def test_update_vacancy_rejects_invalid_salary(
    db_session,
    reference_ids,
):
    vacancy = create_vacancy(
        db_session,
        make_vacancy_data(reference_ids),
    )

    update_data = VacancyUpdate(
        salary_min=Decimal("130000.00"),
    )

    with pytest.raises(ValidationError):
        update_vacancy(db_session, vacancy.id, update_data)

    assert vacancy.salary_min == Decimal("80000.00")


def test_update_vacancy_replaces_skills(db_session, reference_ids):
    vacancy = create_vacancy(
        db_session,
        make_vacancy_data(reference_ids),
    )

    update_data = VacancyUpdate(
        skill_ids=[reference_ids["python_skill_id"]],
    )

    update_vacancy(db_session, vacancy.id, update_data)

    db_session.expire(vacancy, ["vacancy_skills"])

    assert [item.skill_id for item in vacancy.vacancy_skills] == [
        reference_ids["python_skill_id"]
    ]


def test_update_nonexistent_vacancy(db_session):
    update_data = VacancyUpdate(
        salary_usd=Decimal("110000.00"),
    )

    result = update_vacancy(db_session, 99999, update_data)

    assert result is None


def test_delete_vacancy(db_session, reference_ids):
    vacancy = create_vacancy(
        db_session,
        make_vacancy_data(reference_ids),
    )

    result = delete_vacancy(db_session, vacancy.id)

    assert result is True
    assert db_session.get(Vacancy, vacancy.id) is None
    assert (
        db_session.scalars(
            select(VacancySkill).where(VacancySkill.vacancy_id == vacancy.id)
        ).all()
        == []
    )


def test_delete_nonexistent_vacancy(db_session):
    result = delete_vacancy(db_session, 99999)

    assert result is False
