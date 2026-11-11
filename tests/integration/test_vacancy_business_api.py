from decimal import Decimal

from ai_jobs.services.vacancy import create_vacancy
from tests.unit.test_vacancy_service import make_vacancy_data


def create_test_vacancy(db_session, reference_ids, **overrides):
    """Create and persist a vacancy for API tests."""
    data = make_vacancy_data(reference_ids, **overrides)
    vacancy = create_vacancy(db_session, data)
    db_session.commit()
    db_session.refresh(vacancy)
    return vacancy


def test_get_similar_vacancies_api(client, db_session, reference_ids):
    first = create_test_vacancy(db_session, reference_ids)
    create_test_vacancy(
        db_session,
        reference_ids,
        salary_usd=Decimal("110000.00"),
    )

    response = client.get(f"/api/v1/vacancies/{first.id}/similar")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["shared_skills_count"] == 2


def test_get_similar_vacancies_api_not_found(client):
    response = client.get("/api/v1/vacancies/999/similar")

    assert response.status_code == 404


def test_compare_vacancies_api(client, db_session, reference_ids):
    first = create_test_vacancy(
        db_session,
        reference_ids,
        salary_usd=Decimal("100000.00"),
    )
    second = create_test_vacancy(
        db_session,
        reference_ids,
        salary_usd=Decimal("120000.00"),
    )

    response = client.post(
        "/api/v1/vacancies/compare",
        json={"vacancy_ids": [first.id, second.id]},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["vacancies"]) == 2
    assert Decimal(data["average_salary"]) == Decimal("110000.00")
    assert Decimal(data["salary_difference"]) == Decimal("20000.00")


def test_compare_vacancies_api_not_found(client, db_session, reference_ids):
    vacancy = create_test_vacancy(db_session, reference_ids)

    response = client.post(
        "/api/v1/vacancies/compare",
        json={"vacancy_ids": [vacancy.id, 999]},
    )

    assert response.status_code == 404


def test_compare_vacancies_api_rejects_duplicate_ids(client, db_session, reference_ids):
    vacancy = create_test_vacancy(db_session, reference_ids)

    response = client.post(
        "/api/v1/vacancies/compare",
        json={"vacancy_ids": [vacancy.id, vacancy.id]},
    )

    assert response.status_code == 422
