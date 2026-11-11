from statistics import median

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ai_jobs.models.country import Country
from ai_jobs.models.skill import Skill
from ai_jobs.models.specialization import Specialization
from ai_jobs.models.vacancy import Vacancy
from ai_jobs.models.vacancy_skill import VacancySkill


def get_analytics_summary(db: Session) -> dict:
    """Return general statistics about vacancies."""

    total_vacancies = db.scalar(select(func.count(Vacancy.id))) or 0

    average_salary = db.scalar(select(func.avg(Vacancy.salary_usd)))

    salaries = db.scalars(select(Vacancy.salary_usd).order_by(Vacancy.salary_usd)).all()

    median_salary = median(salaries) if salaries else None

    countries_count = (
        db.scalar(select(func.count(func.distinct(Vacancy.country_id)))) or 0
    )

    specializations_count = (
        db.scalar(select(func.count(func.distinct(Vacancy.specialization_id)))) or 0
    )

    return {
        "total_vacancies": total_vacancies,
        "average_salary": average_salary,
        "median_salary": median_salary,
        "countries_count": countries_count,
        "specializations_count": specializations_count,
    }


def get_salary_by_specialization(db: Session) -> list[dict]:
    """Return salary statistics grouped by specialization."""

    statement = (
        select(
            Specialization.name.label("specialization"),
            func.count(Vacancy.id).label("vacancies_count"),
            func.avg(Vacancy.salary_usd).label("average_salary"),
            func.min(Vacancy.salary_usd).label("min_salary"),
            func.max(Vacancy.salary_usd).label("max_salary"),
        )
        .join(
            Vacancy,
            Vacancy.specialization_id == Specialization.id,
        )
        .group_by(Specialization.id, Specialization.name)
        .order_by(func.avg(Vacancy.salary_usd).desc())
    )

    return [dict(row._mapping) for row in db.execute(statement).all()]


def get_top_skills(db: Session, limit: int = 10) -> list[dict]:
    """Return the most demanded skills."""

    statement = (
        select(
            Skill.name.label("skill"),
            func.count(VacancySkill.vacancy_id).label("vacancies_count"),
        )
        .join(
            VacancySkill,
            VacancySkill.skill_id == Skill.id,
        )
        .group_by(Skill.id, Skill.name)
        .order_by(
            func.count(VacancySkill.vacancy_id).desc(),
            Skill.name.asc(),
        )
        .limit(limit)
    )

    return [dict(row._mapping) for row in db.execute(statement).all()]


def get_demand_by_country(db: Session) -> list[dict]:
    """Return vacancy counts grouped by country."""

    statement = (
        select(
            Country.name.label("country"),
            func.count(Vacancy.id).label("vacancies_count"),
        )
        .join(Vacancy, Vacancy.country_id == Country.id)
        .group_by(Country.id, Country.name)
        .order_by(func.count(Vacancy.id).desc())
    )

    return [dict(row._mapping) for row in db.execute(statement).all()]


def get_demand_by_specialization(db: Session) -> list[dict]:
    """Return vacancy counts grouped by specialization."""

    statement = (
        select(
            Specialization.name.label("specialization"),
            func.count(Vacancy.id).label("vacancies_count"),
        )
        .join(
            Vacancy,
            Vacancy.specialization_id == Specialization.id,
        )
        .group_by(Specialization.id, Specialization.name)
        .order_by(func.count(Vacancy.id).desc())
    )

    return [dict(row._mapping) for row in db.execute(statement).all()]
