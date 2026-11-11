from ai_jobs.etl.validator import SourceVacancy


def extract_skills(skills_required: str) -> list[str]:
    """Split a comma-separated skills string into unique skill names."""
    skills = {skill.strip() for skill in skills_required.split(",") if skill.strip()}

    return sorted(skills, key=str.casefold)


def transform_vacancy(source: SourceVacancy) -> dict:
    """Convert a validated source record into vacancy model fields."""
    return {
        "source_job_id": source.source_job_id,
        "company_size": source.company_size,
        "education_required": source.education_required,
        "experience_level": source.experience_level,
        "years_of_experience": source.years_of_experience,
        "salary_usd": source.salary_usd,
        "salary_min": source.salary_min,
        "salary_max": source.salary_max,
        "salary_category": source.salary_category,
        "bonus_percentage": source.bonus_percentage,
        "equity_offered": source.equity_offered,
        "benefits_value_usd": source.benefits_value_usd,
        "job_openings": source.job_openings,
        "competition_level_applicants": (source.competition_level_applicants),
        "hiring_difficulty": source.hiring_difficulty,
        "work_from_home_available": source.work_from_home_available,
        "remote_work_percentage": source.remote_work_percentage,
        "job_satisfaction": source.job_satisfaction,
        "work_life_balance": source.work_life_balance,
        "ai_investment_company_millions": (source.ai_investment_company_millions),
        "company_ai_maturity": source.company_ai_maturity,
        "job_growth_projection_percentage": (source.job_growth_projection_percentage),
        "automation_risk_percentage": source.automation_risk_percentage,
        "gender_diversity_female_percentage": (
            source.gender_diversity_female_percentage
        ),
        "posted_date": source.posted_date,
        "application_deadline": source.application_deadline,
        "record_created": source.record_created,
        "data_source": source.data_source,
    }


def transform_skills(source: SourceVacancy) -> list[str]:
    """Extract normalized skills from a validated source record."""
    return extract_skills(source.skills_required)
