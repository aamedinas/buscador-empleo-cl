"""Clase base para scrapers de portales de empleo chilenos.

Cada portal implementa `search()`. La clase base centraliza:
- cliente HTTP con timeout, reintentos y User-Agent realista
- espera aleatoria entre requests (politeness delay, no para evadir
  deteccion sino para no sobrecargar el sitio de origen)
- manejo uniforme de errores/timeouts/bloqueos (HTTP 403/429)
- normalizacion a `JobPosting`

IMPORTANTE: los selectores HTML de cada portal son un snapshot al
momento de escribir este codigo y pueden quedar desactualizados ante
cualquier rediseno del sitio. Revisar y ajustar `SELECTORS` en cada
modulo contra el DOM real antes de depender de esto en produccion.
Respetar siempre robots.txt y los Terminos de Servicio del portal.
"""

import asyncio
import random
from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.salary import build_executive_summary, estimate_salary_range
from app.models.job import JobPosting, Portal


class ScraperError(Exception):
    pass


class BlockedError(ScraperError):
    """El portal respondio con 403/429 o un challenge anti-bot."""


class BaseScraper(ABC):
    portal: Portal

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = get_logger(f"scraper.{self.portal.value}")

    def _headers(self) -> dict[str, str]:
        user_agent = random.choice(self.settings.scraping_user_agents)
        return {
            "User-Agent": user_agent,
            "Accept-Language": "es-CL,es;q=0.9",
        }

    async def _polite_delay(self) -> None:
        delay = random.uniform(
            self.settings.scraping_min_delay_seconds,
            self.settings.scraping_max_delay_seconds,
        )
        await asyncio.sleep(delay)

    async def _get(self, client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self.settings.scraping_max_retries + 1):
            try:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    timeout=self.settings.scraping_request_timeout_seconds,
                    **kwargs,
                )
                if response.status_code in (403, 429):
                    raise BlockedError(
                        f"{self.portal.value} respondio {response.status_code} para {url}"
                    )
                response.raise_for_status()
                # httpx a veces adivina mal el charset de estos portales
                # (se ha visto mojibake en texto con tildes); todos
                # declaran contenido en UTF-8, asi que se fuerza aqui.
                response.encoding = "utf-8"
                return response
            except (httpx.TimeoutException, httpx.TransportError, BlockedError) as exc:
                last_exc = exc
                self.logger.warning(
                    "Reintento de scraping",
                    extra={
                        "extra_fields": {
                            "portal": self.portal.value,
                            "url": url,
                            "attempt": attempt + 1,
                            "error": str(exc),
                        }
                    },
                )
                await self._polite_delay()
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _soup(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def _normalize(
        self,
        *,
        title: str,
        company: str,
        location: str,
        url: str,
        published_at=None,
        description: str | None = None,
        industry: str | None = None,
    ) -> JobPosting:
        return JobPosting(
            title=title.strip(),
            company=company.strip() or "No especificado",
            location=location.strip() or "Chile",
            portal=self.portal,
            url=url,
            published_at=published_at,
            summary=build_executive_summary(title, company, description),
            salary_range=estimate_salary_range(title, description),
            industry=industry,
            raw_description=description,
        )

    # Siglas/terminos de rubro ambiguos para un buscador de texto libre:
    # "TI" tambien es el pronombre "ti" (muy comun en avisos de retail,
    # gastronomia, etc. - "trabaja para ti", "un lugar pensado para
    # ti"), asi que como keyword suelta ensucia los resultados en vez
    # de acotarlos. Se expande a una frase sin ambiguedad antes de
    # mandarla al buscador del portal (la etiqueta que ve el usuario en
    # `industry` no cambia, solo el texto de busqueda).
    _INDUSTRY_QUERY_EXPANSIONS: dict[str, str] = {
        "ti": "tecnologia informatica",
    }

    @classmethod
    def _build_query(cls, role: str, industry: str | None) -> str:
        """Combina cargo + rubro en un unico termino de busqueda. Los
        portales tratados aqui son buscadores de texto simple, no
        soportan filtros estructurados por rubro, asi que el rubro se
        suma como palabra clave adicional."""
        if not industry:
            return role
        expanded = cls._INDUSTRY_QUERY_EXPANSIONS.get(industry.strip().lower(), industry)
        return f"{role} {expanded}".strip()

    @abstractmethod
    async def search(
        self, role: str, location: str | None, limit: int, industry: str | None = None
    ) -> list[JobPosting]:
        """Busca `role` (combinado con `industry` si se da) en el portal
        y retorna hasta `limit` resultados normalizados."""
        raise NotImplementedError


class StubScraper(BaseScraper):
    """Base para portales que no se scrapean en esta version (ver README):
    LinkedIn e Indeed Chile tienen anti-bot fuerte y ToS que prohiben
    explicitamente el scraping. Esta clase deja la interfaz correcta
    para conectar su API oficial o un proveedor de datos autorizado."""

    stub_reason: str = "Portal no implementado por restricciones de ToS/anti-bot."

    async def search(
        self, role: str, location: str | None, limit: int, industry: str | None = None
    ) -> list[JobPosting]:
        self.logger.info(
            "Scraper en modo stub",
            extra={
                "extra_fields": {
                    "portal": self.portal.value,
                    "role": role,
                    "reason": self.stub_reason,
                }
            },
        )
        return []
