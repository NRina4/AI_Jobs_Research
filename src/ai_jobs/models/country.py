from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_jobs.db.base import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    continent_id: Mapped[int] = mapped_column(
        ForeignKey("continents.id"),
        nullable=False,
        index=True,
    )

    continent: Mapped["Continent"] = relationship(
        back_populates="countries",
    )
