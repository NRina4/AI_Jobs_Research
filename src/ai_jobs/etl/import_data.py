import argparse
import logging
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_jobs.db.session import SessionLocal
from ai_jobs.etl.reader import read_csv
from ai_jobs.etl.transformer import transform_skills, transform_vacancy
from ai_jobs.etl.validator import SourceVacancy
from ai_jobs.models import (
    CertificationRequirement,
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

logger = logging.getLogger(__name__)


def get_or_create(
    session: Session,
    model: type,
    name: str,
    **extra_fields,
):
    """Find a lookup record by name or create it."""
    instance = session.scalar(select(model).where(model.name == name))

    if instance is None:
        instance = model(name=name, **extra_fields)
        session.add(instance)
        session.flush()

    return instance


def import_csv(source_path: Path) -> dict[str, int]:
    """Validate, transform and load CSV records into the database."""
    stats = {
        "total": 0,
        "loaded": 0,
        "skipped": 0,
        "rejected": 0,
    }

    with SessionLocal() as session, session.begin():
        for line_number, row in read_csv(source_path):
            stats["total"] += 1

            try:
                source = SourceVacancy.model_validate(row)
            except ValidationError as error:
                stats["rejected"] += 1
                logger.warning(
                    "Rejected CSV row %s: %s",
                    line_number,
                    error,
                )
                continue

            existing = session.scalar(
                select(Vacancy).where(Vacancy.source_job_id == source.source_job_id)
            )

            if existing is not None:
                stats["skipped"] += 1
                continue

            continent = get_or_create(
                session,
                Continent,
                source.continent,
            )

            country = get_or_create(
                session,
                Country,
                source.country,
                continent_id=continent.id,
            )

            if country.continent_id != continent.id:
                raise ValueError(
                    f"Country '{source.country}' is already associated "
                    f"with another continent."
                )

            company = get_or_create(
                session,
                Company,
                source.company,
            )

            job_title = get_or_create(
                session,
                JobTitle,
                source.job_title,
            )

            specialization = get_or_create(
                session,
                Specialization,
                source.ai_specialization,
            )

            industry = get_or_create(
                session,
                Industry,
                source.industry,
            )

            employment_type = get_or_create(
                session,
                EmploymentType,
                source.job_type,
            )

            certification = None
            if source.required_certifications:
                certification = get_or_create(
                    session,
                    CertificationRequirement,
                    source.required_certifications,
                )

            vacancy_data = transform_vacancy(source)

            vacancy = Vacancy(
                **vacancy_data,
                company_id=company.id,
                country_id=country.id,
                job_title_id=job_title.id,
                specialization_id=specialization.id,
                industry_id=industry.id,
                employment_type_id=employment_type.id,
                certification_requirement_id=(
                    certification.id if certification else None
                ),
            )

            session.add(vacancy)
            session.flush()

            for skill_name in transform_skills(source):
                skill = get_or_create(
                    session,
                    Skill,
                    skill_name,
                )

                session.add(
                    VacancySkill(
                        vacancy_id=vacancy.id,
                        skill_id=skill.id,
                    )
                )

            stats["loaded"] += 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Import AI job market data from CSV.")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/global_ai_jobs_2026.csv"),
        help="Path to the source CSV file.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    stats = import_csv(args.source)

    logger.info(
        "Import finished. Total: %s, loaded: %s, skipped: %s, rejected: %s",
        stats["total"],
        stats["loaded"],
        stats["skipped"],
        stats["rejected"],
    )


if __name__ == "__main__":
    main()
