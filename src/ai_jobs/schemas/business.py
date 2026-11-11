from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_jobs.schemas.vacancy import VacancyRead


class SimilarVacancyRead(BaseModel):
    """A similar vacancy with the number of shared skills."""

    vacancy: VacancyRead
    shared_skills_count: int


class CompareVacanciesRequest(BaseModel):
    """Request schema for comparing vacancies."""

    model_config = ConfigDict(json_schema_extra={"example": {"vacancy_ids": [1, 2]}})

    vacancy_ids: list[int] = Field(min_length=2, max_length=5)

    @model_validator(mode="after")
    def validate_unique_ids(self):
        if len(self.vacancy_ids) != len(set(self.vacancy_ids)):
            raise ValueError("Vacancy IDs must be unique.")

        return self


class CompareVacanciesResponse(BaseModel):
    """Response schema for vacancy comparison."""

    vacancies: list[VacancyRead]
    average_salary: Decimal
    salary_difference: Decimal
    highest_paid_vacancy_id: int
    lowest_paid_vacancy_id: int
