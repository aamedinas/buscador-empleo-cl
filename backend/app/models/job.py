from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class Portal(str, Enum):
    TRABAJANDO = "trabajando.com"
    LABORUM = "laborum"
    COMPUTRABAJO = "computrabajo"
    GETONBRD = "getonbrd"
    LINKEDIN = "linkedin"
    INDEED = "indeed_cl"


class SalaryRange(BaseModel):
    min_clp: int | None = Field(default=None, ge=0)
    max_clp: int | None = Field(default=None, ge=0)
    is_estimated: bool = True
    source: str = Field(description="keyword_heuristic | published | historical_average")


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    portal: Portal
    url: HttpUrl
    published_at: date | None = None
    summary: str = Field(description="Resumen ejecutivo de 2 lineas generado automaticamente")
    salary_range: SalaryRange
    industry: str | None = Field(
        default=None, description="Rubro usado en la busqueda que encontro esta oferta, si se filtro por rubro"
    )
    raw_description: str | None = Field(default=None, exclude=True)


class JobSearchRequest(BaseModel):
    roles: list[str] = Field(
        default_factory=lambda: [
            "Sub-gerente",
            "Lider de produccion",
            "Jefe de infraestructura",
            "Gerente",
        ]
    )
    portals: list[Portal] | None = Field(
        default=None, description="Si es None, se consultan todos los portales habilitados"
    )
    industries: list[str] | None = Field(
        default=None,
        description="Rubros opcionales (ej. Tecnologia, Retail). Si se dan, se cruzan con cada rol",
    )
    location: str | None = Field(default=None, description="Filtro opcional de ciudad/region")
    limit_per_portal: int = Field(default=20, ge=1, le=100)


class PortalResult(BaseModel):
    portal: Portal
    ok: bool
    count: int
    error: str | None = None


class JobSearchResponse(BaseModel):
    total: int
    results: list[JobPosting]
    portal_status: list[PortalResult]
