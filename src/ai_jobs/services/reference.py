from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_jobs.models.certification_requirement import CertificationRequirement
from ai_jobs.models.company import Company
from ai_jobs.models.country import Country
from ai_jobs.models.employment_type import EmploymentType
from ai_jobs.models.industry import Industry
from ai_jobs.models.job_title import JobTitle
from ai_jobs.models.skill import Skill
from ai_jobs.models.specialization import Specialization


def get_countries(db: Session) -> list[Country]:
    statement = select(Country).order_by(Country.name)
    return list(db.scalars(statement).all())


def get_specializations(db: Session) -> list[Specialization]:
    statement = select(Specialization).order_by(Specialization.name)
    return list(db.scalars(statement).all())


def get_skills(db: Session) -> list[Skill]:
    statement = select(Skill).order_by(Skill.name)
    return list(db.scalars(statement).all())


def get_industries(db: Session) -> list[Industry]:
    statement = select(Industry).order_by(Industry.name)
    return list(db.scalars(statement).all())


def get_companies(db: Session) -> list[Company]:
    statement = select(Company).order_by(Company.name)
    return list(db.scalars(statement).all())


def get_job_titles(db: Session) -> list[JobTitle]:
    statement = select(JobTitle).order_by(JobTitle.name)
    return list(db.scalars(statement).all())


def get_employment_types(db: Session) -> list[EmploymentType]:
    statement = select(EmploymentType).order_by(EmploymentType.name)
    return list(db.scalars(statement).all())


def get_certification_requirements(
    db: Session,
) -> list[CertificationRequirement]:
    statement = select(CertificationRequirement).order_by(CertificationRequirement.name)
    return list(db.scalars(statement).all())
