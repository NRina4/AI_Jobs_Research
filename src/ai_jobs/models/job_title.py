from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ai_jobs.db.base import Base


class JobTitle(Base):
    __tablename__ = "job_titles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )
