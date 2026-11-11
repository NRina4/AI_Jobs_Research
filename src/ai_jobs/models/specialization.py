from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ai_jobs.db.base import Base


class Specialization(Base):
    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )
