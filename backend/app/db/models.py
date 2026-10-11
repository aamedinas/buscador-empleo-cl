from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class JobPostingRecord(Base):
    """Cache de resultados de busqueda, para no re-scrapear en cada
    consulta y para poder exportar historicos a CSV."""

    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300))
    company: Mapped[str] = mapped_column(String(300))
    location: Mapped[str] = mapped_column(String(300))
    portal: Mapped[str] = mapped_column(String(50), index=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    published_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    summary: Mapped[str] = mapped_column(String(1000))
    salary_min_clp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max_clp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_is_estimated: Mapped[bool] = mapped_column(default=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
