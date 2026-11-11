from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from ai_jobs.models import (
        Company,
        Country,
        EmploymentType,
        Industry,
        JobTitle,
        Specialization,
        VacancySkill,
    )

from ai_jobs.db.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    __table_args__ = (
        CheckConstraint(
            "salary_min <= salary_max",
            name="salary_min_lte_salary_max",
        ),
        CheckConstraint(
            "salary_usd >= salary_min AND salary_usd <= salary_max",
            name="salary_usd_within_range",
        ),
        CheckConstraint(
            "application_deadline >= posted_date",
            name="deadline_after_posted",
        ),
        CheckConstraint(
            "years_of_experience >= 0",
            name="years_experience_nonnegative",
        ),
        CheckConstraint(
            "job_openings >= 0 AND competition_level_applicants >= 0",
            name="vacancy_counts_nonnegative",
        ),
        CheckConstraint(
            "bonus_percentage BETWEEN 0 AND 100",
            name="bonus_percentage_range",
        ),
        CheckConstraint(
            "remote_work_percentage BETWEEN 0 AND 100",
            name="remote_work_percentage_range",
        ),
        CheckConstraint(
            "job_growth_projection_percentage BETWEEN 0 AND 100",
            name="job_growth_projection_range",
        ),
        CheckConstraint(
            "automation_risk_percentage BETWEEN 0 AND 100",
            name="automation_risk_range",
        ),
        CheckConstraint(
            "gender_diversity_female_percentage BETWEEN 0 AND 100",
            name="gender_diversity_range",
        ),
        CheckConstraint(
            "hiring_difficulty BETWEEN 1 AND 10",
            name="hiring_difficulty_range",
        ),
        CheckConstraint(
            "job_satisfaction BETWEEN 1 AND 10",
            name="job_satisfaction_range",
        ),
        CheckConstraint(
            "work_life_balance BETWEEN 1 AND 10",
            name="work_life_balance_range",
        ),
        CheckConstraint(
            "company_ai_maturity BETWEEN 1 AND 10",
            name="company_ai_maturity_range",
        ),
        CheckConstraint(
            "salary_min >= 0",
            name="salary_min_nonnegative",
        ),
        CheckConstraint(
            "benefits_value_usd >= 0",
            name="benefits_value_nonnegative",
        ),
        CheckConstraint(
            "ai_investment_company_millions >= 0",
            name="ai_investment_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    source_job_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"),
        nullable=False,
        index=True,
    )
    job_title_id: Mapped[int] = mapped_column(
        ForeignKey("job_titles.id"),
        nullable=False,
        index=True,
    )
    specialization_id: Mapped[int] = mapped_column(
        ForeignKey("specializations.id"),
        nullable=False,
        index=True,
    )
    industry_id: Mapped[int] = mapped_column(
        ForeignKey("industries.id"),
        nullable=False,
        index=True,
    )
    employment_type_id: Mapped[int] = mapped_column(
        ForeignKey("employment_types.id"),
        nullable=False,
        index=True,
    )
    certification_requirement_id: Mapped[int | None] = mapped_column(
        ForeignKey("certification_requirements.id"),
        nullable=True,
    )

    company_size: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    education_required: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    experience_level: Mapped[str] = mapped_column(String(100), nullable=False)
    years_of_experience: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    salary_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    salary_min: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    salary_max: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    salary_category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    bonus_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    equity_offered: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    benefits_value_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    job_openings: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    competition_level_applicants: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    hiring_difficulty: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
    work_from_home_available: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    remote_work_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    job_satisfaction: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
    work_life_balance: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )

    ai_investment_company_millions: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )
    company_ai_maturity: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )

    job_growth_projection_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    automation_risk_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    gender_diversity_female_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    posted_date: Mapped[date] = mapped_column(Date, nullable=False)
    application_deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    record_created: Mapped[date] = mapped_column(Date, nullable=False)

    data_source: Mapped[str] = mapped_column(String(150), nullable=False)

    company: Mapped["Company"] = relationship()
    country: Mapped["Country"] = relationship()
    job_title: Mapped["JobTitle"] = relationship()
    specialization: Mapped["Specialization"] = relationship()
    industry: Mapped["Industry"] = relationship()
    employment_type: Mapped["EmploymentType"] = relationship()
    certification_requirement: Mapped["CertificationRequirement | None"] = (
        relationship()
    )

    vacancy_skills: Mapped[list["VacancySkill"]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
    )
