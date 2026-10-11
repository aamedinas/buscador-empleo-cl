from urllib.parse import quote

import httpx

from app.models.job import JobPosting, Portal
from app.scrapers.base import BaseScraper

# GetOnBrd es mayoritariamente roles tech/producto; se incluye como
# portal opcional segun lo pedido. Es Rails server-rendered (no SPA),
# por lo que si trae resultados utilizables en el HTML inicial.
# Selectores verificados contra el DOM real el 2026-10-10 (busqueda
# "gerente"). Pueden quedar desactualizados ante un rediseno del sitio.
SELECTORS = {
    "result_card": "a.results-item",
    "title": "h4.results-list-title strong",
    "company": "div.results-list-info > div.size0 strong",
    "location": "span.js-locations-tooltip",
}


class GetOnBrdScraper(BaseScraper):
    portal = Portal.GETONBRD
    SEARCH_URL = "https://www.getonbrd.com/jobs/search?query={query}&country=cl"

    async def search(
        self, role: str, location: str | None, limit: int, industry: str | None = None
    ) -> list[JobPosting]:
        query = self._build_query(role, industry)
        url = self.SEARCH_URL.format(query=quote(query))
        postings: list[JobPosting] = []

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await self._get(client, url)
            except Exception as exc:  # noqa: BLE001
                self.logger.error(
                    "Fallo al consultar portal",
                    extra={"extra_fields": {"portal": self.portal.value, "error": str(exc)}},
                )
                raise

            soup = self._soup(response.text)
            cards = soup.select(SELECTORS["result_card"])[:limit]

            for card in cards:
                title_el = card.select_one(SELECTORS["title"])
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = card.get("href", "")
                job_url = href if href.startswith("http") else f"https://www.getonbrd.com{href}"

                company_el = card.select_one(SELECTORS["company"])

                location_el = card.select_one(SELECTORS["location"])
                location_text = ""
                if location_el:
                    direct_text = location_el.find(string=True, recursive=False)
                    location_text = direct_text.strip() if direct_text else ""

                if location and location_text and location.lower() not in location_text.lower():
                    continue

                postings.append(
                    self._normalize(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "",
                        location=location_text,
                        url=job_url,
                        published_at=None,
                        description=card.get_text(" ", strip=True),
                        industry=industry,
                    )
                )

            await self._polite_delay()

        return postings
