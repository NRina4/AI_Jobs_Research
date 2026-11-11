from datetime import date
from decimal import Decimal

from pydantic import (
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class VacancyCreate(BaseModel):
    """Schema for creating a vacancy."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": 1,
                "country_id": 1,
                "job_title_id": 1,
                "specialization_id": 1,
                "industry_id": 1,
                "employment_type_id": 1,
                "experience_level": "Middle",
                "salary_usd": "90000.00",
                "salary_min": "80000.00",
                "salary_max": "100000.00",
                "skill_ids": [1, 2],
            }
        }
    )

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

    company_size: str | None = None
    education_required: str | None = None
    experience_level: str = Field(min_length=1, max_length=100)
    years_of_experience: Decimal | None = Field(default=None, ge=0)

    salary_usd: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    salary_category: str | None = None

    bonus_percentage: Decimal | None = Field(default=None, ge=0, le=100)
    equity_offered: bool | None = None
    benefits_value_usd: Decimal | None = Field(default=None, ge=0)

    job_openings: int | None = Field(default=None, ge=0)
    competition_level_applicants: int | None = Field(default=None, ge=0)

    hiring_difficulty: Decimal | None = Field(default=None, ge=1, le=10)
    work_from_home_available: bool | None = None
    remote_work_percentage: Decimal | None = Field(default=None, ge=0, le=100)

    job_satisfaction: Decimal | None = Field(default=None, ge=1, le=10)
    work_life_balance: Decimal | None = Field(default=None, ge=1, le=10)

    ai_investment_company_millions: Decimal | None = Field(default=None, ge=0)
    company_ai_maturity: Decimal | None = Field(default=None, ge=1, le=10)

    job_growth_projection_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    automation_risk_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    gender_diversity_female_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    posted_date: date = Field(default_factory=date.today)
    application_deadline: date | None = None
    record_created: date = Field(default_factory=date.today)
    data_source: str = Field(default="Manual entry", max_length=150)

    skill_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_salary_and_dates(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("Minimum salary cannot exceed maximum salary.")

        if self.salary_min is not None and self.salary_usd < self.salary_min:
            raise ValueError("Salary cannot be lower than minimum salary.")

        if self.salary_max is not None and self.salary_usd > self.salary_max:
            raise ValueError("Salary cannot exceed maximum salary.")

        if (
            self.application_deadline is not None
            and self.application_deadline < self.posted_date
        ):
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

    company_size: str | None = None
    education_required: str | None = None
    experience_level: str | None = Field(default=None, min_length=1, max_length=100)
    years_of_experience: Decimal | None = Field(default=None, ge=0)

    salary_usd: Decimal | None = Field(default=None, ge=0)
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    salary_category: str | None = None

    bonus_percentage: Decimal | None = Field(default=None, ge=0, le=100)
    equity_offered: bool | None = None
    benefits_value_usd: Decimal | None = Field(default=None, ge=0)

    job_openings: int | None = Field(default=None, ge=0)
    competition_level_applicants: int | None = Field(default=None, ge=0)

    hiring_difficulty: Decimal | None = Field(default=None, ge=1, le=10)
    work_from_home_available: bool | None = None
    remote_work_percentage: Decimal | None = Field(default=None, ge=0, le=100)

    job_satisfaction: Decimal | None = Field(default=None, ge=1, le=10)
    work_life_balance: Decimal | None = Field(default=None, ge=1, le=10)

    ai_investment_company_millions: Decimal | None = Field(default=None, ge=0)
    company_ai_maturity: Decimal | None = Field(default=None, ge=1, le=10)

    job_growth_projection_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    automation_risk_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    gender_diversity_female_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    posted_date: date | None = None
    application_deadline: date | None = None
    record_created: date | None = None
    data_source: str | None = Field(default=None, max_length=150)

    skill_ids: list[int] | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        required_fields = {
            "company_id",
            "country_id",
            "job_title_id",
            "specialization_id",
            "industry_id",
            "employment_type_id",
            "experience_level",
            "salary_usd",
            "posted_date",
            "record_created",
            "data_source",
            "skill_ids",
        }

        for field_name in self.model_fields_set & required_fields:
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

    company_name: str = Field(validation_alias=AliasPath("company", "name"))
    country_name: str = Field(validation_alias=AliasPath("country", "name"))
    job_title_name: str = Field(validation_alias=AliasPath("job_title", "name"))
    specialization_name: str = Field(
        validation_alias=AliasPath("specialization", "name")
    )

    company_size: str | None
    education_required: str | None
    experience_level: str
    years_of_experience: Decimal | None

    salary_usd: Decimal
    salary_min: Decimal | None
    salary_max: Decimal | None
    salary_category: str | None

    bonus_percentage: Decimal | None
    equity_offered: bool | None
    benefits_value_usd: Decimal | None

    job_openings: int | None
    competition_level_applicants: int | None

    hiring_difficulty: Decimal | None
    work_from_home_available: bool | None
    remote_work_percentage: Decimal | None

    job_satisfaction: Decimal | None
    work_life_balance: Decimal | None

    ai_investment_company_millions: Decimal | None
    company_ai_maturity: Decimal | None

    job_growth_projection_percentage: Decimal | None
    automation_risk_percentage: Decimal | None
    gender_diversity_female_percentage: Decimal | None

    posted_date: date
    application_deadline: date | None
    record_created: date
    data_source: str

    skill_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="wrap")
    @classmethod
    def populate_skill_ids(cls, data: object, handler):
        """Build model and populate skill_ids from ORM relations when present."""
        model = handler(data)
        if not isinstance(data, dict):
            vacancy_skills = getattr(data, "vacancy_skills", None)
            if vacancy_skills is not None:
                model.skill_ids = [item.skill_id for item in vacancy_skills]
        return model
