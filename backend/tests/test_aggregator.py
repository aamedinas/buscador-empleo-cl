from unittest.mock import patch

import pytest

from app.models.job import JobPosting, JobSearchRequest, Portal, SalaryRange
from app.scrapers.aggregator import search_all_portals
from app.scrapers.base import BaseScraper


def _posting(url: str, industry: str | None) -> JobPosting:
    return JobPosting(
        title="Gerente de Tecnologia",
        company="Empresa Demo",
        location="Santiago",
        portal=Portal.COMPUTRABAJO,
        url=url,
        summary="Gerente de Tecnologia en Empresa Demo.\nSin descripcion.",
        salary_range=SalaryRange(min_clp=None, max_clp=None, is_estimated=True, source="historical_average"),
        industry=industry,
    )


class _RecordingScraper(BaseScraper):
    portal = Portal.COMPUTRABAJO
    calls: list[tuple[str, str | None]] = []

    async def search(self, role, location, limit, industry=None):
        _RecordingScraper.calls.append((role, industry))
        return []


@pytest.mark.asyncio
async def test_search_crosses_roles_and_industries():
    _RecordingScraper.calls = []
    request = JobSearchRequest(
        roles=["Gerente", "Jefe de infraestructura"],
        industries=["Tecnologia", "Retail"],
        portals=[Portal.COMPUTRABAJO],
    )

    with patch("app.scrapers.aggregator.SCRAPERS", {Portal.COMPUTRABAJO: _RecordingScraper}):
        await search_all_portals(request)

    assert sorted(_RecordingScraper.calls) == sorted(
        [
            ("Gerente", "Tecnologia"),
            ("Gerente", "Retail"),
            ("Jefe de infraestructura", "Tecnologia"),
            ("Jefe de infraestructura", "Retail"),
        ]
    )


@pytest.mark.asyncio
async def test_search_without_industries_passes_none():
    _RecordingScraper.calls = []
    request = JobSearchRequest(roles=["Gerente"], portals=[Portal.COMPUTRABAJO])

    with patch("app.scrapers.aggregator.SCRAPERS", {Portal.COMPUTRABAJO: _RecordingScraper}):
        await search_all_portals(request)

    assert _RecordingScraper.calls == [("Gerente", None)]


def test_build_query_combines_role_and_industry():
    assert BaseScraper._build_query("Gerente", "Tecnologia") == "Gerente Tecnologia"
    assert BaseScraper._build_query("Gerente", None) == "Gerente"


def test_build_query_expands_ambiguous_ti():
    # "TI" sola es tambien el pronombre "ti" (muy comun en avisos de
    # retail/gastronomia); debe expandirse a algo sin ambiguedad antes
    # de mandarlo al buscador del portal.
    assert BaseScraper._build_query("Gerente", "TI") == "Gerente tecnologia informatica"
    assert BaseScraper._build_query("Gerente", "ti") == "Gerente tecnologia informatica"
    # El rubro mostrado al usuario (JobPosting.industry) sigue siendo
    # "TI" tal cual lo eligio; solo la query de busqueda se expande.


class _DuplicateUrlScraper(BaseScraper):
    portal = Portal.COMPUTRABAJO

    async def search(self, role, location, limit, industry=None):
        # Simula que el mismo aviso aparece para dos rubros distintos.
        return [_posting("https://www.computrabajo.cl/oferta-123", industry)]


@pytest.mark.asyncio
async def test_search_dedupes_same_url_across_industries():
    request = JobSearchRequest(
        roles=["Gerente"],
        industries=["Tecnologia", "TI"],
        portals=[Portal.COMPUTRABAJO],
    )

    with patch("app.scrapers.aggregator.SCRAPERS", {Portal.COMPUTRABAJO: _DuplicateUrlScraper}):
        postings, statuses = await search_all_portals(request)

    assert len(postings) == 1
    # El status por portal si refleja el total crudo encontrado (2),
    # para no esconder cuanto trabajo hizo el scraper.
    assert statuses[0].count == 2
