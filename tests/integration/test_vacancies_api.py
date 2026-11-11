from tests.unit.test_vacancy_service import make_vacancy_data


def create_test_vacancy(client, reference_ids):
    """Create a vacancy through the API and return its ID."""

    vacancy_data = make_vacancy_data(reference_ids)

    response = client.post(
        "/api/v1/vacancies",
        json=vacancy_data.model_dump(
            mode="json",
            exclude={"skill_ids"},
        ),
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_vacancy_api(client, reference_ids):
    vacancy_data = make_vacancy_data(reference_ids)

    response = client.post(
        "/api/v1/vacancies",
        json=vacancy_data.model_dump(
            mode="json",
            exclude={"skill_ids"},
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["company_id"] == reference_ids["company_id"]
    assert data["salary_usd"] == "100000.00"


def test_get_vacancies_api(client, reference_ids):
    create_test_vacancy(client, reference_ids)

    response = client.get("/api/v1/vacancies")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["salary_usd"] == "100000.00"


def test_get_vacancy_by_id_api(client, reference_ids):
    vacancy_id = create_test_vacancy(client, reference_ids)

    response = client.get(f"/api/v1/vacancies/{vacancy_id}")

    assert response.status_code == 200
    assert response.json()["id"] == vacancy_id
    assert response.json()["salary_usd"] == "100000.00"


def test_update_vacancy_api(client, reference_ids):
    vacancy_id = create_test_vacancy(client, reference_ids)

    response = client.patch(
        f"/api/v1/vacancies/{vacancy_id}",
        json={
            "salary_usd": "110000",
            "salary_min": "90000",
            "salary_max": "130000",
        },
    )

    assert response.status_code == 200
    assert response.json()["salary_usd"] == "110000.00"
    assert response.json()["salary_min"] == "90000.00"
    assert response.json()["salary_max"] == "130000.00"


def test_delete_vacancy_api(client, reference_ids):
    vacancy_id = create_test_vacancy(client, reference_ids)

    delete_response = client.delete(f"/api/v1/vacancies/{vacancy_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/vacancies/{vacancy_id}")

    assert get_response.status_code == 404


def test_get_nonexistent_vacancy_api(client):
    response = client.get("/api/v1/vacancies/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vacancy not found"


def test_update_nonexistent_vacancy_api(client):
    response = client.patch(
        "/api/v1/vacancies/99999",
        json={"salary_usd": "110000"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vacancy not found"


def test_delete_nonexistent_vacancy_api(client):
    response = client.delete("/api/v1/vacancies/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vacancy not found"


def test_create_vacancy_with_invalid_data_api(client):
    response = client.post(
        "/api/v1/vacancies",
        json={"salary_usd": -100},
    )

    assert response.status_code == 422


def test_filter_vacancies_by_salary_api(client, reference_ids):
    create_test_vacancy(client, reference_ids)

    response = client.get("/api/v1/vacancies", params={"min_salary": 110000})

    assert response.status_code == 200
    assert response.json() == []


def test_sort_vacancies_by_salary_api(client, reference_ids):
    first_id = create_test_vacancy(client, reference_ids)
    second_id = create_test_vacancy(client, reference_ids)

    client.patch(
        f"/api/v1/vacancies/{second_id}",
        json={
            "salary_usd": "120000",
            "salary_min": "100000",
            "salary_max": "140000",
        },
    )

    response = client.get(
        "/api/v1/vacancies",
        params={"sort_by": "salary_usd", "sort_order": "desc"},
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == second_id
    assert response.json()[1]["id"] == first_id


def test_paginate_vacancies_api(client, reference_ids):
    create_test_vacancy(client, reference_ids)
    create_test_vacancy(client, reference_ids)

    response = client.get(
        "/api/v1/vacancies",
        params={"offset": 1, "limit": 1},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_vacancies_with_invalid_salary_range_api(client):
    response = client.get(
        "/api/v1/vacancies",
        params={
            "min_salary": 150000,
            "max_salary": 100000,
        },
    )

    assert response.status_code == 422


def test_filter_vacancies_with_invalid_sort_field_api(client):
    response = client.get(
        "/api/v1/vacancies",
        params={"sort_by": "invalid_field"},
    )

    assert response.status_code == 422
