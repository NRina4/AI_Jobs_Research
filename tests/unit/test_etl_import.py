import csv

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from ai_jobs.etl import import_data
from ai_jobs.models import Company, Skill, Vacancy, VacancySkill
from tests.unit.etl_helpers import make_source_row


def write_csv(tmp_path, rows):
    """Write test rows to a temporary CSV file."""
    source = tmp_path / "jobs.csv"

    with source.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return source


def patch_session_factory(monkeypatch, db_session):
    """Use the test database for ETL imports."""
    test_session_factory = sessionmaker(
        bind=db_session.get_bind(),
        expire_on_commit=False,
    )
    monkeypatch.setattr(import_data, "SessionLocal", test_session_factory)


def test_import_csv_loads_valid_record(tmp_path, db_session, monkeypatch):
    patch_session_factory(monkeypatch, db_session)
    source = write_csv(tmp_path, [make_source_row()])

    stats = import_data.import_csv(source)

    assert stats == {
        "total": 1,
        "loaded": 1,
        "skipped": 0,
        "rejected": 0,
    }

    assert db_session.scalar(select(func.count(Vacancy.id))) == 1
    assert db_session.scalar(select(func.count(Company.id))) == 1
    assert db_session.scalar(select(func.count(Skill.id))) == 2
    assert db_session.scalar(select(func.count(VacancySkill.vacancy_id))) == 2


def test_import_csv_skips_duplicate_records(tmp_path, db_session, monkeypatch):
    patch_session_factory(monkeypatch, db_session)
    source = write_csv(tmp_path, [make_source_row()])

    first_stats = import_data.import_csv(source)
    second_stats = import_data.import_csv(source)

    assert first_stats["loaded"] == 1
    assert second_stats == {
        "total": 1,
        "loaded": 0,
        "skipped": 1,
        "rejected": 0,
    }

    assert db_session.scalar(select(func.count(Vacancy.id))) == 1


def test_import_csv_rejects_invalid_record(tmp_path, db_session, monkeypatch):
    patch_session_factory(monkeypatch, db_session)
    invalid_row = make_source_row(Equity_Offered="maybe")
    source = write_csv(tmp_path, [invalid_row])

    stats = import_data.import_csv(source)

    assert stats == {
        "total": 1,
        "loaded": 0,
        "skipped": 0,
        "rejected": 1,
    }

    assert db_session.scalar(select(func.count(Vacancy.id))) == 0


def test_import_csv_reuses_existing_lookup_records(
    tmp_path,
    db_session,
    monkeypatch,
):
    patch_session_factory(monkeypatch, db_session)

    first_row = make_source_row()
    second_row = make_source_row(Job_ID="JOB-002")
    source = write_csv(tmp_path, [first_row, second_row])

    stats = import_data.import_csv(source)

    assert stats["loaded"] == 2
    assert db_session.scalar(select(func.count(Vacancy.id))) == 2
    assert db_session.scalar(select(func.count(Company.id))) == 1
    assert db_session.scalar(select(func.count(Skill.id))) == 2
