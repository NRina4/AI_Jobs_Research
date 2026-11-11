from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ai_jobs.db.session import get_db
from ai_jobs.schemas.analytics import (
    AnalyticsSummary,
    DemandAnalytics,
    SalaryBySpecialization,
    TopSkill,
)
from ai_jobs.services.analytics import (
    get_analytics_summary,
    get_demand_by_country,
    get_demand_by_specialization,
    get_salary_by_specialization,
    get_top_skills,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)):
    return get_analytics_summary(db)


@router.get("/salaries", response_model=list[SalaryBySpecialization])
def analytics_salaries(db: Session = Depends(get_db)):
    return get_salary_by_specialization(db)


@router.get("/top-skills", response_model=list[TopSkill])
def analytics_top_skills(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_top_skills(db, limit=limit)


@router.get("/demand", response_model=DemandAnalytics)
def analytics_demand(db: Session = Depends(get_db)):
    return {
        "by_country": get_demand_by_country(db),
        "by_specialization": get_demand_by_specialization(db),
    }
