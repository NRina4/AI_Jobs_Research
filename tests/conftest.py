import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

import ai_jobs.models  # noqa: F401
from ai_jobs.db.base import Base


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for each test."""

    engine = create_engine("sqlite:///:memory:")

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
