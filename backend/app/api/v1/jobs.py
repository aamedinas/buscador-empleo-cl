import csv
import io
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import get_current_user
from app.db.models import JobPostingRecord
from app.db.session import get_db
from app.models.job import JobSearchRequest, JobSearchResponse
from app.scrapers.aggregator import search_all_portals

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = get_logger(__name__)


async def _persist_results(db: AsyncSession, response: JobSearchResponse) -> None:
    for posting in response.results:
        exists = await db.scalar(
            select(JobPostingRecord.id).where(JobPostingRecord.url == str(posting.url))
        )
        if exists:
            continue
        db.add(
            JobPostingRecord(
                title=posting.title,
                company=posting.company,
                location=posting.location,
                portal=posting.portal.value,
                industry=posting.industry,
                url=str(posting.url),
                published_at=posting.published_at,
                summary=posting.summary,
                salary_min_clp=posting.salary_range.min_clp,
                salary_max_clp=posting.salary_range.max_clp,
                salary_is_estimated=posting.salary_range.is_estimated,
            )
        )
    await db.commit()


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(
    request: JobSearchRequest,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> JobSearchResponse:
    logger.info(
        "Busqueda de empleos iniciada",
        extra={
            "extra_fields": {
                "user": user.get("preferred_username", user.get("sub")),
                "roles": request.roles,
                "portals": [p.value for p in request.portals] if request.portals else "all",
            }
        },
    )

    postings, portal_status = await search_all_portals(request)
    response = JobSearchResponse(total=len(postings), results=postings, portal_status=portal_status)

    try:
        await _persist_results(db, response)
    except Exception as exc:  # noqa: BLE001 - la persistencia no debe tumbar la respuesta al usuario
        logger.warning("No se pudo persistir resultados", extra={"extra_fields": {"error": str(exc)}})

    return response


@router.post("/search/csv")
async def search_jobs_csv(
    request: JobSearchRequest,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> StreamingResponse:
    postings, _ = await search_all_portals(request)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["titulo", "empresa", "ubicacion", "portal", "rubro", "resumen", "salario_min_clp", "salario_max_clp", "url", "fecha_publicacion"]
    )
    for posting in postings:
        writer.writerow(
            [
                posting.title,
                posting.company,
                posting.location,
                posting.portal.value,
                posting.industry or "",
                posting.summary.replace("\n", " | "),
                posting.salary_range.min_clp,
                posting.salary_range.max_clp,
                str(posting.url),
                posting.published_at or "",
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ofertas_empleo.csv"},
    )
