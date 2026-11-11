from uuid import uuid4

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
from ai_jobs.schemas.vacancy import VacancyCreate
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
