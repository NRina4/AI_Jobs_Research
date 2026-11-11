from ai_jobs.models.certification_requirement import CertificationRequirement


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


def test_get_companies_api(client, reference_ids):
    response = client.get("/api/v1/companies")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Company"


def test_get_job_titles_api(client, reference_ids):
    response = client.get("/api/v1/job-titles")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "AI Engineer"


def test_get_employment_types_api(client, reference_ids):
    response = client.get("/api/v1/employment-types")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Full-time"


def test_get_certification_requirements_api(client, db_session):
    requirement = CertificationRequirement(name="AWS Certification")
    db_session.add(requirement)
    db_session.commit()

    response = client.get("/api/v1/certification-requirements")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "AWS Certification"
