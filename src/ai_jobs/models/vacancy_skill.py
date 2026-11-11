from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_jobs.db.base import Base


class VacancySkill(Base):
    __tablename__ = "vacancy_skills"

    __table_args__ = (
        UniqueConstraint(
            "vacancy_id",
            "skill_id",
            name="uq_vacancy_skills_vacancy_skill",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vacancy: Mapped["Vacancy"] = relationship(
        back_populates="vacancy_skills",
    )
    skill: Mapped["Skill"] = relationship(
        back_populates="vacancy_skills",
    )
