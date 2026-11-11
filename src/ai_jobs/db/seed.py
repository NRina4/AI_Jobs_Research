import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from ai_jobs.db.session import SessionLocal
from ai_jobs.models import (
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


def seed_database() -> bool:
    """Insert a small set of demo data if the database is empty."""
    with SessionLocal() as session, session.begin():
        if (session.scalar(select(func.count(Vacancy.id))) or 0) > 0:
            logger.info("Seed skipped: vacancies already exist.")
            return False

        continent = Continent(name="Europe")
        country = Country(name="Poland", continent=continent)
        company = Company(name="AI Labs")
        job_title = JobTitle(name="ML Engineer")
        specialization = Specialization(name="Machine Learning")
        industry = Industry(name="Technology")
        employment_type = EmploymentType(name="Full-time")
        python_skill = Skill(name="Python")
        sql_skill = Skill(name="SQL")

        session.add_all(
            [
                continent,
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
        session.flush()

        vacancy = Vacancy(
            source_job_id="seed-001",
            company_id=company.id,
            country_id=country.id,
            job_title_id=job_title.id,
            specialization_id=specialization.id,
            industry_id=industry.id,
            employment_type_id=employment_type.id,
            experience_level="Middle",
            years_of_experience=Decimal("3.0"),
            salary_usd=Decimal("90000.00"),
            salary_min=Decimal("80000.00"),
            salary_max=Decimal("100000.00"),
            salary_category="High",
            posted_date=date.today(),
            record_created=date.today(),
            data_source="Seed data",
        )
        session.add(vacancy)
        session.flush()

        session.add_all(
            [
                VacancySkill(vacancy_id=vacancy.id, skill_id=python_skill.id),
                VacancySkill(vacancy_id=vacancy.id, skill_id=sql_skill.id),
            ]
        )

    logger.info("Seed completed: demo data inserted.")
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    seed_database()


if __name__ == "__main__":
    main()
