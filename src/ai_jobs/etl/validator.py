from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceVacancy(BaseModel):
    """Validated representation of one source CSV row."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    source_job_id: str = Field(alias="Job_ID", min_length=1)
    job_title: str = Field(alias="Job_Title", min_length=1)
    ai_specialization: str = Field(alias="AI_Specialization", min_length=1)
    industry: str = Field(alias="Industry", min_length=1)
    company: str = Field(alias="Company", min_length=1)
    company_size: str = Field(alias="Company_Size", min_length=1)
    country: str = Field(alias="Country", min_length=1)
    continent: str = Field(alias="Continent", min_length=1)
    education_required: str = Field(alias="Education_Required", min_length=1)
    experience_level: str = Field(alias="Experience_Level", min_length=1)

    years_of_experience: Decimal = Field(
        alias="Years_of_Experience",
        ge=0,
    )

    salary_usd: Decimal = Field(alias="Salary_USD", ge=0)
    salary_min: Decimal = Field(alias="Salary_Min", ge=0)
    salary_max: Decimal = Field(alias="Salary_Max", ge=0)
    salary_category: str = Field(alias="Salary_Category", min_length=1)

    bonus_percentage: Decimal = Field(alias="Bonus_%", ge=0, le=100)
    equity_offered: bool = Field(alias="Equity_Offered")
    benefits_value_usd: Decimal = Field(alias="Benefits_Value_USD", ge=0)

    skills_required: str = Field(alias="Skills_Required", min_length=1)
    required_certifications: str | None = Field(
        default=None,
        alias="Required_Certifications",
    )

    job_openings: int = Field(alias="Job_Openings", ge=0)
    competition_level_applicants: int = Field(
        alias="Competition_Level_Applicants",
        ge=0,
    )
    hiring_difficulty: Decimal = Field(
        alias="Hiring_Difficulty_1_10",
        ge=1,
        le=10,
    )

    job_type: str = Field(alias="Job_Type", min_length=1)
    remote_work_percentage: Decimal = Field(
        alias="Remote_Work_%",
        ge=0,
        le=100,
    )
    work_from_home_available: bool = Field(alias="Work_From_Home_Available")

    job_satisfaction: Decimal = Field(
        alias="Job_Satisfaction_1_10",
        ge=1,
        le=10,
    )
    work_life_balance: Decimal = Field(
        alias="Work_Life_Balance_1_10",
        ge=1,
        le=10,
    )

    ai_investment_company_millions: Decimal = Field(
        alias="AI_Investment_Company_Millions",
        ge=0,
    )
    company_ai_maturity: Decimal = Field(
        alias="Company_AI_Maturity_1_10",
        ge=1,
        le=10,
    )

    job_growth_projection_percentage: Decimal = Field(
        alias="Job_Growth_Projection_%",
        ge=0,
        le=100,
    )
    automation_risk_percentage: Decimal = Field(
        alias="Automation_Risk_%",
        ge=0,
        le=100,
    )
    gender_diversity_female_percentage: Decimal = Field(
        alias="Gender_Diversity_%_Female",
        ge=0,
        le=100,
    )

    posted_date: date = Field(alias="Posted_Date")
    application_deadline: date = Field(alias="Application_Deadline")
    record_created: date = Field(alias="Record_Created")
    data_source: str = Field(alias="Data_Source", min_length=1)

    @field_validator("required_certifications", mode="before")
    @classmethod
    def empty_certification_to_none(cls, value: object) -> object:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value

    @field_validator(
        "equity_offered",
        "work_from_home_available",
        mode="before",
    )
    @classmethod
    def parse_boolean(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)) and value in (0, 1):
            return bool(value)

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in {"true", "yes", "1"}:
                return True

            if normalized in {"false", "no", "0"}:
                return False

        raise ValueError(f"Invalid boolean value: {value!r}")

    @model_validator(mode="after")
    def validate_salary_and_dates(self) -> "SourceVacancy":
        if self.salary_min > self.salary_max:
            raise ValueError("Salary_Min cannot be greater than Salary_Max.")

        if not self.salary_min <= self.salary_usd <= self.salary_max:
            raise ValueError("Salary_USD must be between Salary_Min and Salary_Max.")

        if self.application_deadline < self.posted_date:
            raise ValueError("Application_Deadline cannot be earlier than Posted_Date.")

        return self
