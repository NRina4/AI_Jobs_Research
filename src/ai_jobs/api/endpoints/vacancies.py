from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai_jobs.db.session import get_db
from ai_jobs.schemas.business import (
    CompareVacanciesRequest,
    CompareVacanciesResponse,
    SimilarVacancyRead,
)
from ai_jobs.schemas.vacancy import (
    VacancyCreate,
    VacancyRead,
    VacancyUpdate,
)
from ai_jobs.services.exceptions import ReferenceNotFoundError
from ai_jobs.services.vacancy import (
    compare_vacancies,
    create_vacancy,
    delete_vacancy,
    get_similar_vacancies,
    get_vacancies,
    get_vacancy,
    update_vacancy,
)

router = APIRouter(
    prefix="/vacancies",
    tags=["Vacancies"],
)


@router.get("", response_model=list[VacancyRead])
def read_vacancies(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    country_id: int | None = Query(default=None, ge=1),
    specialization_id: int | None = Query(default=None, ge=1),
    employment_type_id: int | None = Query(default=None, ge=1),
    experience_level: str | None = Query(default=None, min_length=1),
    min_salary: Decimal | None = Query(default=None, ge=0),
    max_salary: Decimal | None = Query(default=None, ge=0),
    sort_by: Literal[
        "id",
        "salary_usd",
        "posted_date",
        "years_of_experience",
        "job_satisfaction",
    ] = Query(default="id"),
    sort_order: Literal["asc", "desc"] = Query(default="asc"),
    db: Session = Depends(get_db),
):
    """Get vacancies with filtering, sorting and pagination."""

    if min_salary is not None and max_salary is not None and min_salary > max_salary:
        raise HTTPException(
            status_code=422,
            detail="min_salary cannot be greater than max_salary",
        )

    return get_vacancies(
        db,
        offset=offset,
        limit=limit,
        country_id=country_id,
        specialization_id=specialization_id,
        employment_type_id=employment_type_id,
        experience_level=experience_level,
        min_salary=min_salary,
        max_salary=max_salary,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{vacancy_id}", response_model=VacancyRead)
def read_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db),
):
    """Get a vacancy by its ID."""

    vacancy = get_vacancy(db, vacancy_id)

    if vacancy is None:
        raise HTTPException(
            status_code=404,
            detail="Vacancy not found",
        )

    return vacancy


@router.post("", response_model=VacancyRead, status_code=201)
def create_new_vacancy(
    vacancy_data: VacancyCreate,
    db: Session = Depends(get_db),
):
    """Create a new vacancy."""

    try:
        vacancy = create_vacancy(db, vacancy_data)
        db.commit()
        db.refresh(vacancy)

    except ReferenceNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Vacancy conflicts with an existing record",
        ) from exc

    return vacancy


@router.patch("/{vacancy_id}", response_model=VacancyRead)
def update_existing_vacancy(
    vacancy_id: int,
    vacancy_data: VacancyUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an existing vacancy."""

    try:
        vacancy = update_vacancy(db, vacancy_id, vacancy_data)

        if vacancy is None:
            raise HTTPException(
                status_code=404,
                detail="Vacancy not found",
            )

        db.commit()
        db.refresh(vacancy)

    except ReferenceNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Vacancy conflicts with an existing record",
        ) from exc

    return vacancy


@router.delete("/{vacancy_id}", status_code=204)
def delete_existing_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db),
):
    """Delete an existing vacancy."""

    deleted = delete_vacancy(db, vacancy_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Vacancy not found",
        )

    db.commit()

    return Response(status_code=204)


@router.get(
    "/{vacancy_id}/similar",
    response_model=list[SimilarVacancyRead],
)
def read_similar_vacancies(
    vacancy_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Find vacancies similar to the selected vacancy."""

    vacancies = get_similar_vacancies(
        db,
        vacancy_id=vacancy_id,
        limit=limit,
    )

    if vacancies is None:
        raise HTTPException(
            status_code=404,
            detail="Vacancy not found",
        )

    return vacancies


@router.post(
    "/compare",
    response_model=CompareVacanciesResponse,
)
def compare_selected_vacancies(
    request: CompareVacanciesRequest,
    db: Session = Depends(get_db),
):
    """Compare two to five selected vacancies."""

    result = compare_vacancies(
        db,
        vacancy_ids=request.vacancy_ids,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="One or more vacancies not found",
        )

    return result
