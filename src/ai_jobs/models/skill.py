from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_jobs.db.base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    vacancy_skills: Mapped[list["VacancySkill"]] = relationship(
        back_populates="skill",
    )
