from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_jobs.db.session import get_db
from ai_jobs.schemas.reference import (
    CountryRead,
    IndustryRead,
    SkillRead,
    SpecializationRead,
)
from ai_jobs.services.reference import (
    get_countries,
    get_industries,
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
