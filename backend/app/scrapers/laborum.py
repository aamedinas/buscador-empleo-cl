from app.models.job import Portal
from app.scrapers.base import StubScraper


class LaborumScraper(StubScraper):
    """Laborum.cl es una SPA (React, `id="root"`): el HTML inicial
    verificado en vivo el 2026-10-10 no contiene ninguna oferta, ningun
    bloque de datos embebido ni texto relacionado a busqueda ("aviso",
    "oferta", "empleo" no aparecen); el listado se pide via JS despues
    de la carga. No hay payload server-side que parsear como en
    Trabajando.cl, asi que requeriria directamente un navegador
    headless (Selenium/Playwright) o encontrar y usar su API interna
    (no documentada publicamente).

    Se deja como stub para no fingir una integracion que en la
    practica siempre devuelve cero resultados de forma silenciosa.
    """

    portal = Portal.LABORUM
    stub_reason = (
        "Laborum.cl es una SPA sin datos en el HTML inicial; el listado se carga via "
        "JS despues de hidratar. Requiere navegador headless o su API interna (no "
        "documentada)."
    )
