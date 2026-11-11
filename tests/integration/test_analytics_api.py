from decimal import Decimal

from ai_jobs.services.vacancy import create_vacancy
from tests.unit.test_vacancy_service import make_vacancy_data


def create_test_vacancy(db_session, reference_ids, **overrides):
    """Create a vacancy directly in the test database."""
    vacancy_data = make_vacancy_data(reference_ids, **overrides)
    return create_vacancy(db_session, vacancy_data)


def test_analytics_summary_api(client, db_session, reference_ids):
    create_test_vacancy(db_session, reference_ids)

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_vacancies"] == 1
    assert data["average_salary"] is not None
    assert Decimal(data["average_salary"]) == Decimal("100000.00")
    assert Decimal(data["median_salary"]) == Decimal("100000.00")
    assert data["countries_count"] == 1
    assert data["specializations_count"] == 1


def test_analytics_salaries_api(client, db_session, reference_ids):
    create_test_vacancy(db_session, reference_ids)

    response = client.get("/api/v1/analytics/salaries")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["specialization"] == "Machine Learning"
    assert data[0]["vacancies_count"] == 1
    assert Decimal(data[0]["average_salary"]) == Decimal("100000.00")


def test_analytics_top_skills_api(client, db_session, reference_ids):
    create_test_vacancy(db_session, reference_ids)

    create_test_vacancy(
        db_session,
        reference_ids,
        skill_ids=[reference_ids["python_skill_id"]],
    )

    response = client.get(
        "/api/v1/analytics/top-skills",
        params={"limit": 1},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["skill"] == "Python"
    assert data[0]["vacancies_count"] == 2


def test_analytics_demand_api(client, db_session, reference_ids):
    create_test_vacancy(db_session, reference_ids)

    response = client.get("/api/v1/analytics/demand")

    assert response.status_code == 200

    data = response.json()

    assert data["by_country"] == [{"country": "Poland", "vacancies_count": 1}]

    assert data["by_specialization"] == [
        {"specialization": "Machine Learning", "vacancies_count": 1}
    ]


def test_analytics_summary_empty_database_api(client):
    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_vacancies"] == 0
    assert data["average_salary"] is None
    assert data["median_salary"] is None
    assert data["countries_count"] == 0
    assert data["specializations_count"] == 0
