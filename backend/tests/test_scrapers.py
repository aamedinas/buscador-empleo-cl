import httpx
import pytest
import respx

from app.scrapers.computrabajo import ComputrabajoScraper
from app.scrapers.getonbrd import GetOnBrdScraper
from app.scrapers.indeed import IndeedScraper
from app.scrapers.laborum import LaborumScraper
from app.scrapers.linkedin import LinkedInScraper
from app.scrapers.trabajando import TrabajandoScraper

# Fragmentos minimos que reproducen la estructura real de cada portal,
# verificada contra el HTML en vivo el 2026-10-10 (ver SELECTORS en
# cada modulo). No son el HTML completo, solo lo necesario para que el
# parser encuentre los campos.

FAKE_COMPUTRABAJO_HTML = """
<html><body>
<article class="box_offer outstanding">
    <h2 class="fs18 fwB prB">
        <a class="js-o-link fc_base" href="/ofertas-de-trabajo/oferta-123">Gerente Comercial</a>
    </h2>
    <p class="dFlex vm_fx fs16 fc_base mt5">
        <a class="fc_base t_ellipsis" href="https://cl.computrabajo.com/empresa-demo" offer-grid-article-company-url>
            Empresa Demo SpA
        </a>
    </p>
    <p class="fs16 fc_base mt5">
        <span class="mr10">Santiago, Region Metropolitana</span>
    </p>
    <p class="fs13 fc_aux mt15">Hace 1 hora</p>
</article>
</body></html>
"""

FAKE_GETONBRD_HTML = """
<html><body>
<a class="results-item" href="https://www.getonbrd.com/jobs/ops/jefe-de-infraestructura-empresa-demo-santiago">
    <div class="results-list-info">
        <h4 class="results-list-title"><strong class="pr-3">Jefe de Infraestructura</strong> <span>Full time</span></h4>
        <div class="size0 flex gap-1 items-center">
            <strong>Empresa Demo SpA</strong>
            <span><span class="location">
                <span class="js-locations-tooltip">
                    Santiago
                    <div class="location-tooltip-content hide">Tooltip largo irrelevante</div>
                </span>
            </span></span>
        </div>
    </div>
</a>
</body></html>
"""


@pytest.mark.asyncio
async def test_linkedin_stub_returns_empty():
    scraper = LinkedInScraper()
    results = await scraper.search(role="Gerente", location=None, limit=10)
    assert results == []


@pytest.mark.asyncio
async def test_indeed_stub_returns_empty():
    scraper = IndeedScraper()
    results = await scraper.search(role="Gerente", location=None, limit=10)
    assert results == []


@pytest.mark.asyncio
async def test_trabajando_stub_returns_empty():
    """Trabajando.cl es una SPA Nuxt sin datos parseables en el HTML
    inicial (ver docstring del scraper); queda como stub documentado."""
    scraper = TrabajandoScraper()
    results = await scraper.search(role="Gerente", location=None, limit=10)
    assert results == []


@pytest.mark.asyncio
async def test_laborum_stub_returns_empty():
    """Laborum.cl es una SPA React sin datos en el HTML inicial; queda
    como stub documentado."""
    scraper = LaborumScraper()
    results = await scraper.search(role="Gerente", location=None, limit=10)
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_computrabajo_scraper_parses_and_normalizes():
    respx.get(url__regex=r"https://www\.computrabajo\.cl/.*").mock(
        return_value=httpx.Response(200, text=FAKE_COMPUTRABAJO_HTML)
    )

    scraper = ComputrabajoScraper()
    results = await scraper.search(role="Gerente", location=None, limit=10)

    assert len(results) == 1
    posting = results[0]
    assert posting.title == "Gerente Comercial"
    assert posting.company == "Empresa Demo SpA"
    assert "Santiago" in posting.location
    assert str(posting.url) == "https://www.computrabajo.cl/ofertas-de-trabajo/oferta-123"
    assert posting.salary_range.min_clp is not None
    assert "Gerente Comercial" in posting.summary


@pytest.mark.asyncio
@respx.mock
async def test_computrabajo_scraper_handles_blocked_response():
    respx.get(url__regex=r"https://www\.computrabajo\.cl/.*").mock(
        return_value=httpx.Response(403, text="blocked")
    )

    scraper = ComputrabajoScraper()

    with pytest.raises(Exception):
        await scraper.search(role="Gerente", location=None, limit=10)


@pytest.mark.asyncio
@respx.mock
async def test_getonbrd_scraper_parses_and_normalizes():
    respx.get(url__regex=r"https://www\.getonbrd\.com/.*").mock(
        return_value=httpx.Response(200, text=FAKE_GETONBRD_HTML)
    )

    scraper = GetOnBrdScraper()
    results = await scraper.search(role="Jefe de infraestructura", location=None, limit=10)

    assert len(results) == 1
    posting = results[0]
    assert posting.title == "Jefe de Infraestructura"
    assert posting.company == "Empresa Demo SpA"
    assert posting.location == "Santiago"
    assert "Tooltip largo irrelevante" not in posting.location
    assert str(posting.url) == "https://www.getonbrd.com/jobs/ops/jefe-de-infraestructura-empresa-demo-santiago"
