from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.job import JobPosting, Portal, PortalResult, SalaryRange


def _fake_posting() -> JobPosting:
    return JobPosting(
        title="Gerente de Operaciones",
        company="Empresa Demo",
        location="Santiago",
        portal=Portal.COMPUTRABAJO,
        url="https://www.computrabajo.cl/empleo/1",
        published_at=None,
        summary="Gerente de Operaciones en Empresa Demo.\nSin descripcion detallada disponible en el portal de origen.",
        salary_range=SalaryRange(min_clp=3_800_000, max_clp=7_500_000, is_estimated=True, source="historical_average"),
    )


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_search_jobs_without_keycloak_in_dev_mode():
    fake_posting = _fake_posting()
    fake_status = [PortalResult(portal=Portal.COMPUTRABAJO, ok=True, count=1)]

    with patch(
        "app.api.v1.jobs.search_all_portals",
        new=AsyncMock(return_value=([fake_posting], fake_status)),
    ), patch("app.api.v1.jobs._persist_results", new=AsyncMock()):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/jobs/search",
                json={"roles": ["Gerente"], "limit_per_portal": 5},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["results"][0]["title"] == "Gerente de Operaciones"
    assert body["portal_status"][0]["ok"] is True
