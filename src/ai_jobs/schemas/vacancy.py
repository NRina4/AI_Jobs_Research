from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VacancyCreate(BaseModel):
    """Schema for creating a vacancy."""

    source_job_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    company_id: int = Field(gt=0)
    country_id: int = Field(gt=0)
    job_title_id: int = Field(gt=0)
    specialization_id: int = Field(gt=0)
    industry_id: int = Field(gt=0)
    employment_type_id: int = Field(gt=0)
    certification_requirement_id: int | None = Field(default=None, gt=0)

    company_size: str = Field(min_length=1, max_length=50)
    education_required: str = Field(min_length=1, max_length=100)
    experience_level: str = Field(min_length=1, max_length=100)
    years_of_experience: Decimal = Field(ge=0, max_digits=5, decimal_places=2)

    salary_usd: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    salary_min: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    salary_max: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    salary_category: str = Field(min_length=1, max_length=50)

    bonus_percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    equity_offered: bool
    benefits_value_usd: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    job_openings: int = Field(ge=0)
    competition_level_applicants: int = Field(ge=0)

    hiring_difficulty: Decimal = Field(ge=1, le=10, max_digits=4, decimal_places=2)
    work_from_home_available: bool
    remote_work_percentage: Decimal = Field(
        ge=0, le=100, max_digits=5, decimal_places=2
    )
    job_satisfaction: Decimal = Field(ge=1, le=10, max_digits=4, decimal_places=2)
    work_life_balance: Decimal = Field(ge=1, le=10, max_digits=4, decimal_places=2)

    ai_investment_company_millions: Decimal = Field(
        ge=0, max_digits=14, decimal_places=2
    )
    company_ai_maturity: Decimal = Field(ge=1, le=10, max_digits=4, decimal_places=2)

    job_growth_projection_percentage: Decimal = Field(
        ge=0, le=100, max_digits=5, decimal_places=2
    )
    automation_risk_percentage: Decimal = Field(
        ge=0, le=100, max_digits=5, decimal_places=2
    )
    gender_diversity_female_percentage: Decimal = Field(
        ge=0, le=100, max_digits=5, decimal_places=2
    )

    posted_date: date
    application_deadline: date
    record_created: date
    data_source: str = Field(min_length=1, max_length=150)

    skill_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_salary_and_dates(self):
        if self.salary_min > self.salary_max:
            raise ValueError("Minimum salary cannot exceed maximum salary.")

        if not self.salary_min <= self.salary_usd <= self.salary_max:
            raise ValueError("Salary must be within the specified range.")

        if self.application_deadline < self.posted_date:
            raise ValueError("Application deadline cannot precede posted date.")

        if any(skill_id <= 0 for skill_id in self.skill_ids):
            raise ValueError("Skill IDs must be positive.")

        if len(self.skill_ids) != len(set(self.skill_ids)):
            raise ValueError("Skill IDs must be unique.")

        return self


class VacancyUpdate(BaseModel):
    """Schema for partially updating a vacancy."""

    company_id: int | None = Field(default=None, gt=0)
    country_id: int | None = Field(default=None, gt=0)
    job_title_id: int | None = Field(default=None, gt=0)
    specialization_id: int | None = Field(default=None, gt=0)
    industry_id: int | None = Field(default=None, gt=0)
    employment_type_id: int | None = Field(default=None, gt=0)
    certification_requirement_id: int | None = Field(default=None, gt=0)

    company_size: str | None = Field(default=None, min_length=1, max_length=50)
    education_required: str | None = Field(default=None, min_length=1, max_length=100)
    experience_level: str | None = Field(default=None, min_length=1, max_length=100)
    years_of_experience: Decimal | None = Field(
        default=None, ge=0, max_digits=5, decimal_places=2
    )

    salary_usd: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    salary_min: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    salary_max: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    salary_category: str | None = Field(default=None, min_length=1, max_length=50)

    bonus_percentage: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    equity_offered: bool | None = None
    benefits_value_usd: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )

    job_openings: int | None = Field(default=None, ge=0)
    competition_level_applicants: int | None = Field(default=None, ge=0)

    hiring_difficulty: Decimal | None = Field(
        default=None, ge=1, le=10, max_digits=4, decimal_places=2
    )
    work_from_home_available: bool | None = None
    remote_work_percentage: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    job_satisfaction: Decimal | None = Field(
        default=None, ge=1, le=10, max_digits=4, decimal_places=2
    )
    work_life_balance: Decimal | None = Field(
        default=None, ge=1, le=10, max_digits=4, decimal_places=2
    )

    ai_investment_company_millions: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=2
    )
    company_ai_maturity: Decimal | None = Field(
        default=None, ge=1, le=10, max_digits=4, decimal_places=2
    )

    job_growth_projection_percentage: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    automation_risk_percentage: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    gender_diversity_female_percentage: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )

    posted_date: date | None = None
    application_deadline: date | None = None
    record_created: date | None = None
    data_source: str | None = Field(default=None, min_length=1, max_length=150)

    skill_ids: list[int] | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        nullable_fields = {"certification_requirement_id"}

        for field_name in self.model_fields_set - nullable_fields:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null.")

        if self.skill_ids is not None:
            if any(skill_id <= 0 for skill_id in self.skill_ids):
                raise ValueError("Skill IDs must be positive.")

            if len(self.skill_ids) != len(set(self.skill_ids)):
                raise ValueError("Skill IDs must be unique.")

        return self


class VacancyRead(BaseModel):
    """Schema for returning vacancy data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_job_id: str

    company_id: int
    country_id: int
    job_title_id: int
    specialization_id: int
    industry_id: int
    employment_type_id: int
    certification_requirement_id: int | None

    company_size: str
    education_required: str
    experience_level: str
    years_of_experience: Decimal

    salary_usd: Decimal
    salary_min: Decimal
    salary_max: Decimal
    salary_category: str

    bonus_percentage: Decimal
    equity_offered: bool
    benefits_value_usd: Decimal

    job_openings: int
    competition_level_applicants: int

    hiring_difficulty: Decimal
    work_from_home_available: bool
    remote_work_percentage: Decimal
    job_satisfaction: Decimal
    work_life_balance: Decimal

    ai_investment_company_millions: Decimal
    company_ai_maturity: Decimal

    job_growth_projection_percentage: Decimal
    automation_risk_percentage: Decimal
    gender_diversity_female_percentage: Decimal

    posted_date: date
    application_deadline: date
    record_created: date
    data_source: str
