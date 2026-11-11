from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_jobs.db.base import Base


class Continent(Base):
    __tablename__ = "continents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    countries: Mapped[list["Country"]] = relationship(
        back_populates="continent",
    )
