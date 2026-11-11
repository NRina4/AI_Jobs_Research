import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai_jobs.db.base import Base
from ai_jobs.db.session import get_db
from ai_jobs.main import app
from ai_jobs.models import (
    Company,
    Continent,
    Country,
    EmploymentType,
    Industry,
    JobTitle,
    Skill,
    Specialization,
)


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for each test."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    """Create a test client using the isolated test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


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
