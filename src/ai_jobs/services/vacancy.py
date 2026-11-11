from uuid import uuid4

from sqlalchemy import select
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
) -> list[Vacancy]:
    """Get a paginated list of vacancies."""

    statement = select(Vacancy).order_by(Vacancy.id).offset(offset).limit(limit)

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
