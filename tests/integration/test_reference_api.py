def test_get_countries_api(client, reference_ids):
    response = client.get("/api/v1/countries")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Poland"
    assert data[0]["continent_id"] == 1


def test_get_specializations_api(client, reference_ids):
    response = client.get("/api/v1/specializations")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Machine Learning"


def test_get_skills_api(client, reference_ids):
    response = client.get("/api/v1/skills")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert {item["name"] for item in data} == {"Python", "SQL"}


def test_get_industries_api(client, reference_ids):
    response = client.get("/api/v1/industries")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Technology"


def test_get_empty_reference_api(client):
    response = client.get("/api/v1/countries")

    assert response.status_code == 200
    assert response.json() == []
