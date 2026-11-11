from decimal import Decimal

from ai_jobs.services.analytics import (
    get_analytics_summary,
    get_demand_by_country,
    get_demand_by_specialization,
    get_salary_by_specialization,
    get_top_skills,
)
from ai_jobs.services.vacancy import create_vacancy
from tests.unit.test_vacancy_service import make_vacancy_data


def test_analytics_summary_empty_database(db_session):
    result = get_analytics_summary(db_session)

    assert result == {
        "total_vacancies": 0,
        "average_salary": None,
        "median_salary": None,
        "countries_count": 0,
        "specializations_count": 0,
    }


def test_analytics_summary(db_session, reference_ids):
    first_vacancy = make_vacancy_data(
        reference_ids,
        salary_usd=Decimal("100000.00"),
    )
    second_vacancy = make_vacancy_data(
        reference_ids,
        salary_usd=Decimal("200000.00"),
        salary_min=Decimal("180000.00"),
        salary_max=Decimal("220000.00"),
    )

    create_vacancy(db_session, first_vacancy)
    create_vacancy(db_session, second_vacancy)

    result = get_analytics_summary(db_session)

    assert result["total_vacancies"] == 2
    assert result["average_salary"] == Decimal("150000.00")
    assert result["median_salary"] == Decimal("150000.00")
    assert result["countries_count"] == 1
    assert result["specializations_count"] == 1


def test_salary_by_specialization(db_session, reference_ids):
    first_vacancy = make_vacancy_data(
        reference_ids,
        salary_usd=Decimal("100000.00"),
    )
    second_vacancy = make_vacancy_data(
        reference_ids,
        salary_usd=Decimal("200000.00"),
        salary_min=Decimal("180000.00"),
        salary_max=Decimal("220000.00"),
    )

    create_vacancy(db_session, first_vacancy)
    create_vacancy(db_session, second_vacancy)

    result = get_salary_by_specialization(db_session)

    assert len(result) == 1
    assert result[0]["specialization"] == "Machine Learning"
    assert result[0]["vacancies_count"] == 2
    assert result[0]["average_salary"] == Decimal("150000.00")
    assert result[0]["min_salary"] == Decimal("100000.00")
    assert result[0]["max_salary"] == Decimal("200000.00")


def test_top_skills(db_session, reference_ids):
    first_vacancy = make_vacancy_data(
        reference_ids,
        skill_ids=[reference_ids["python_skill_id"]],
    )
    second_vacancy = make_vacancy_data(
        reference_ids,
        skill_ids=[
            reference_ids["python_skill_id"],
            reference_ids["sql_skill_id"],
        ],
    )

    create_vacancy(db_session, first_vacancy)
    create_vacancy(db_session, second_vacancy)

    result = get_top_skills(db_session)

    assert len(result) == 2
    assert result[0] == {
        "skill": "Python",
        "vacancies_count": 2,
    }
    assert result[1] == {
        "skill": "SQL",
        "vacancies_count": 1,
    }


def test_demand_by_country(db_session, reference_ids):
    for _ in range(2):
        create_vacancy(
            db_session,
            make_vacancy_data(reference_ids),
        )

    result = get_demand_by_country(db_session)

    assert result == [
        {
            "country": "Poland",
            "vacancies_count": 2,
        }
    ]


def test_demand_by_specialization(db_session, reference_ids):
    for _ in range(2):
        create_vacancy(
            db_session,
            make_vacancy_data(reference_ids),
        )

    result = get_demand_by_specialization(db_session)

    assert result == [
        {
            "specialization": "Machine Learning",
            "vacancies_count": 2,
        }
    ]
