from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_jobs.db.session import get_db
from ai_jobs.schemas.reference import (
    CountryRead,
    IndustryRead,
    ReferenceItemRead,
    SkillRead,
    SpecializationRead,
)
from ai_jobs.services.reference import (
    get_certification_requirements,
    get_companies,
    get_countries,
    get_employment_types,
    get_industries,
    get_job_titles,
    get_skills,
    get_specializations,
)

router = APIRouter(
    tags=["Reference data"],
)


@router.get("/countries", response_model=list[CountryRead])
def list_countries(db: Session = Depends(get_db)):
    return get_countries(db)


@router.get("/specializations", response_model=list[SpecializationRead])
def list_specializations(db: Session = Depends(get_db)):
    return get_specializations(db)


@router.get("/skills", response_model=list[SkillRead])
def list_skills(db: Session = Depends(get_db)):
    return get_skills(db)


@router.get("/industries", response_model=list[IndustryRead])
def list_industries(db: Session = Depends(get_db)):
    return get_industries(db)


@router.get("/companies", response_model=list[ReferenceItemRead])
def list_companies(db: Session = Depends(get_db)):
    return get_companies(db)


@router.get("/job-titles", response_model=list[ReferenceItemRead])
def list_job_titles(db: Session = Depends(get_db)):
    return get_job_titles(db)


@router.get("/employment-types", response_model=list[ReferenceItemRead])
def list_employment_types(db: Session = Depends(get_db)):
    return get_employment_types(db)


@router.get(
    "/certification-requirements",
    response_model=list[ReferenceItemRead],
)
def list_certification_requirements(db: Session = Depends(get_db)):
    return get_certification_requirements(db)
