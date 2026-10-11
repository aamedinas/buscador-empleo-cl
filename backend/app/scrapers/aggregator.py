import asyncio

from app.core.logging import get_logger
from app.models.job import JobPosting, JobSearchRequest, Portal, PortalResult
from app.scrapers.base import BaseScraper
from app.scrapers.computrabajo import ComputrabajoScraper
from app.scrapers.getonbrd import GetOnBrdScraper
from app.scrapers.indeed import IndeedScraper
from app.scrapers.laborum import LaborumScraper
from app.scrapers.linkedin import LinkedInScraper
from app.scrapers.trabajando import TrabajandoScraper

logger = get_logger(__name__)

SCRAPERS: dict[Portal, type[BaseScraper]] = {
    Portal.TRABAJANDO: TrabajandoScraper,
    Portal.LABORUM: LaborumScraper,
    Portal.COMPUTRABAJO: ComputrabajoScraper,
    Portal.GETONBRD: GetOnBrdScraper,
    Portal.LINKEDIN: LinkedInScraper,
    Portal.INDEED: IndeedScraper,
}


async def _search_one_portal(
    portal: Portal, role: str, location: str | None, limit: int, industry: str | None
) -> tuple[list[JobPosting], PortalResult]:
    scraper_cls = SCRAPERS[portal]
    scraper = scraper_cls()
    try:
        results = await scraper.search(role=role, location=location, limit=limit, industry=industry)
        return results, PortalResult(portal=portal, ok=True, count=len(results))
    except Exception as exc:  # noqa: BLE001 - un portal caido no debe tumbar la busqueda completa
        logger.error(
            "Error consultando portal",
            extra={
                "extra_fields": {
                    "portal": portal.value,
                    "role": role,
                    "industry": industry,
                    "error": str(exc),
                }
            },
        )
        return [], PortalResult(portal=portal, ok=False, count=0, error=str(exc))


def _dedupe_by_url(postings: list[JobPosting]) -> list[JobPosting]:
    """La misma oferta puede salir de mas de una combinacion de
    cargo/rubro (ej. "Gerente Tecnologia" y "Gerente TI" devolviendo el
    mismo aviso); se deduplica por URL quedandose con la primera vez
    que aparecio."""
    seen: set[str] = set()
    unique: list[JobPosting] = []
    for posting in postings:
        key = str(posting.url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(posting)
    return unique


async def search_all_portals(
    request: JobSearchRequest,
) -> tuple[list[JobPosting], list[PortalResult]]:
    portals = request.portals or list(SCRAPERS.keys())
    industries: list[str | None] = list(request.industries) if request.industries else [None]

    tasks = [
        _search_one_portal(portal, role, request.location, request.limit_per_portal, industry)
        for portal in portals
        for role in request.roles
        for industry in industries
    ]

    outcomes = await asyncio.gather(*tasks)

    all_postings: list[JobPosting] = []
    status_by_portal: dict[Portal, PortalResult] = {}

    for postings, status in outcomes:
        all_postings.extend(postings)
        existing = status_by_portal.get(status.portal)
        if existing is None:
            status_by_portal[status.portal] = status
        else:
            status_by_portal[status.portal] = PortalResult(
                portal=status.portal,
                ok=existing.ok and status.ok,
                count=existing.count + status.count,
                error=existing.error or status.error,
            )

    return _dedupe_by_url(all_postings), list(status_by_portal.values())
