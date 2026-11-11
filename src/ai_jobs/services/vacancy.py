from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ai_jobs.models import (
    CertificationRequirement,
    Company,
    Country,
    EmploymentType,
    Industry,
    JobTitle,
    Skill,
    Specialization,
    Vacancy,
    VacancySkill,
)
from ai_jobs.schemas.vacancy import VacancyCreate, VacancyUpdate
from ai_jobs.services.exceptions import ReferenceNotFoundError

REFERENCE_MODELS = {
    "company_id": Company,
    "country_id": Country,
    "job_title_id": JobTitle,
    "specialization_id": Specialization,
    "industry_id": Industry,
    "employment_type_id": EmploymentType,
    "certification_requirement_id": CertificationRequirement,
}


def check_reference(
    db: Session,
    model: type,
    object_id: int | None,
    field_name: str,
) -> None:
    """Check that a referenced record exists."""
    if object_id is None:
        return

    if db.get(model, object_id) is None:
        raise ReferenceNotFoundError(field_name, object_id)


def create_vacancy(
    db: Session,
    vacancy_data: VacancyCreate,
) -> Vacancy:
    """Create a vacancy and connect its required skills."""

    for field_name, model in REFERENCE_MODELS.items():
        check_reference(
            db,
            model,
            getattr(vacancy_data, field_name),
            field_name,
        )

    for skill_id in vacancy_data.skill_ids:
        check_reference(db, Skill, skill_id, "skill_id")

    data = vacancy_data.model_dump(
        exclude={"skill_ids", "source_job_id"},
    )

    source_job_id = vacancy_data.source_job_id or f"manual-{uuid4().hex}"

    vacancy = Vacancy(
        **data,
        source_job_id=source_job_id,
    )

    db.add(vacancy)
    db.flush()

    for skill_id in vacancy_data.skill_ids:
        db.add(
            VacancySkill(
                vacancy_id=vacancy.id,
                skill_id=skill_id,
            )
        )

    db.flush()

    return vacancy


def get_vacancy(db: Session, vacancy_id: int) -> Vacancy | None:
    """Get a vacancy by its ID."""

    return db.get(Vacancy, vacancy_id)


def get_vacancies(
    db: Session,
    offset: int = 0,
    limit: int = 20,
    country_id: int | None = None,
    specialization_id: int | None = None,
    employment_type_id: int | None = None,
    experience_level: str | None = None,
    min_salary: Decimal | None = None,
    max_salary: Decimal | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> list[Vacancy]:
    """Get vacancies with filtering, sorting and pagination."""

    statement = select(Vacancy)

    if country_id is not None:
        statement = statement.where(Vacancy.country_id == country_id)

    if specialization_id is not None:
        statement = statement.where(Vacancy.specialization_id == specialization_id)

    if employment_type_id is not None:
        statement = statement.where(Vacancy.employment_type_id == employment_type_id)

    if experience_level is not None:
        statement = statement.where(Vacancy.experience_level == experience_level)

    if min_salary is not None:
        statement = statement.where(Vacancy.salary_usd >= min_salary)

    if max_salary is not None:
        statement = statement.where(Vacancy.salary_usd <= max_salary)

    sort_columns = {
        "id": Vacancy.id,
        "salary_usd": Vacancy.salary_usd,
        "posted_date": Vacancy.posted_date,
        "years_of_experience": Vacancy.years_of_experience,
        "job_satisfaction": Vacancy.job_satisfaction,
    }

    sort_column = sort_columns[sort_by]

    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    if sort_by != "id":
        statement = statement.order_by(Vacancy.id.asc())

    statement = statement.offset(offset).limit(limit)

    return list(db.scalars(statement).all())


def update_vacancy(
    db: Session,
    vacancy_id: int,
    vacancy_data: VacancyUpdate,
) -> Vacancy | None:
    """Update an existing vacancy."""

    vacancy = db.get(Vacancy, vacancy_id)

    if vacancy is None:
        return None

    update_data = vacancy_data.model_dump(exclude_unset=True)

    current_data = {
        field_name: getattr(vacancy, field_name)
        for field_name in VacancyCreate.model_fields
        if field_name != "skill_ids"
    }

    current_data["skill_ids"] = [item.skill_id for item in vacancy.vacancy_skills]

    merged_data = {**current_data, **update_data}

    # Validate the complete updated vacancy, not only changed fields.
    validated_data = VacancyCreate(**merged_data)

    # Check updated foreign key references.
    for field_name, model in REFERENCE_MODELS.items():
        if field_name in update_data:
            check_reference(
                db,
                model,
                getattr(validated_data, field_name),
                field_name,
            )

    # Check updated skills.
    if "skill_ids" in update_data:
        for skill_id in validated_data.skill_ids:
            check_reference(db, Skill, skill_id, "skill_id")

    # Update scalar fields.
    for field_name, value in update_data.items():
        if field_name != "skill_ids":
            setattr(vacancy, field_name, value)

    # Replace skill associations when skill_ids was provided.
    if "skill_ids" in update_data:
        vacancy.vacancy_skills.clear()
        db.flush()

        vacancy.vacancy_skills.extend(
            [VacancySkill(skill_id=skill_id) for skill_id in validated_data.skill_ids]
        )

    db.flush()

    return vacancy


def delete_vacancy(db: Session, vacancy_id: int) -> bool:
    """Delete a vacancy by its ID."""

    vacancy = db.get(Vacancy, vacancy_id)

    if vacancy is None:
        return False

    db.delete(vacancy)
    db.flush()

    return True


def get_similar_vacancies(
    db: Session,
    vacancy_id: int,
    limit: int = 10,
) -> list[dict] | None:
    """Find vacancies with the same specialization and shared skills."""

    current_vacancy = db.get(Vacancy, vacancy_id)

    if current_vacancy is None:
        return None

    current_skills = select(VacancySkill.skill_id).where(
        VacancySkill.vacancy_id == vacancy_id
    )

    shared_skills_count = func.count(VacancySkill.skill_id)

    statement = (
        select(
            Vacancy,
            shared_skills_count.label("shared_skills_count"),
        )
        .join(VacancySkill, VacancySkill.vacancy_id == Vacancy.id)
        .where(
            Vacancy.specialization_id == current_vacancy.specialization_id,
            Vacancy.id != vacancy_id,
            VacancySkill.skill_id.in_(current_skills),
        )
        .group_by(Vacancy.id)
        .order_by(shared_skills_count.desc(), Vacancy.id.asc())
        .limit(limit)
    )

    results = db.execute(statement).all()

    return [
        {
            "vacancy": vacancy,
            "shared_skills_count": count,
        }
        for vacancy, count in results
    ]


def compare_vacancies(
    db: Session,
    vacancy_ids: list[int],
) -> dict | None:
    """Compare selected vacancies using their salary data."""

    if not 2 <= len(vacancy_ids) <= 5:
        raise ValueError("Between 2 and 5 vacancy IDs must be provided.")

    if len(vacancy_ids) != len(set(vacancy_ids)):
        raise ValueError("Vacancy IDs must be unique.")

    statement = select(Vacancy).where(Vacancy.id.in_(vacancy_ids))
    found_vacancies = db.scalars(statement).all()

    vacancies_by_id = {vacancy.id: vacancy for vacancy in found_vacancies}

    # Return None if at least one requested vacancy does not exist.
    if len(vacancies_by_id) != len(vacancy_ids):
        return None

    # Preserve the order of IDs supplied in the request.
    vacancies = [vacancies_by_id[vacancy_id] for vacancy_id in vacancy_ids]

    salaries = [vacancy.salary_usd for vacancy in vacancies]

    highest_paid = max(vacancies, key=lambda item: item.salary_usd)
    lowest_paid = min(vacancies, key=lambda item: item.salary_usd)

    average_salary = sum(salaries, Decimal(0)) / len(salaries)

    return {
        "vacancies": vacancies,
        "average_salary": average_salary,
        "salary_difference": max(salaries) - min(salaries),
        "highest_paid_vacancy_id": highest_paid.id,
        "lowest_paid_vacancy_id": lowest_paid.id,
    }
