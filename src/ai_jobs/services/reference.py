from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_jobs.models.country import Country
from ai_jobs.models.industry import Industry
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
