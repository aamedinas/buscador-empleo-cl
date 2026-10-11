from urllib.parse import quote

import httpx

from app.models.job import JobPosting, Portal
from app.scrapers.base import BaseScraper

# Selectores verificados contra el DOM real de computrabajo.cl el
# 2026-10-10 (busqueda "gerente"). Pueden quedar desactualizados ante
# un rediseno del sitio; revisar si los resultados dejan de parsear.
SELECTORS = {
    "result_card": "article.box_offer",
    "title": "h2 a.js-o-link",
    "company": "a[offer-grid-article-company-url]",
    "location": "p.fs16.fc_base.mt5:not(.dFlex)",
    "date": "p.fs13.fc_aux.mt15",
}


class ComputrabajoScraper(BaseScraper):
    portal = Portal.COMPUTRABAJO
    SEARCH_URL = "https://www.computrabajo.cl/trabajo-de-{query}"

    async def search(
        self, role: str, location: str | None, limit: int, industry: str | None = None
    ) -> list[JobPosting]:
        query = self._build_query(role, industry)
        url = self.SEARCH_URL.format(query=quote(query.lower().replace(" ", "-")))
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
                href = title_el.get("href", "")
                job_url = href if href.startswith("http") else f"https://www.computrabajo.cl{href}"

                company_el = card.select_one(SELECTORS["company"])
                location_el = card.select_one(SELECTORS["location"])

                if location and location_el and location.lower() not in location_el.get_text(strip=True).lower():
                    continue

                postings.append(
                    self._normalize(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "",
                        location=location_el.get_text(strip=True) if location_el else "",
                        url=job_url,
                        published_at=None,
                        description=card.get_text(" ", strip=True),
                        industry=industry,
                    )
                )

            await self._polite_delay()

        return postings
