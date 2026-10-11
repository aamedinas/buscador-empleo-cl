from app.models.job import Portal
from app.scrapers.base import StubScraper


class TrabajandoScraper(StubScraper):
    """Trabajando.cl es una SPA Nuxt: el HTML inicial no contiene las
    ofertas como elementos parseables, sino un payload interno
    (`__NUXT_DATA__`) en el formato de serializacion propio de Nuxt
    ("devalue"), con referencias por indice en vez de JSON plano.
    Verificado en vivo el 2026-10-10: la pagina de busqueda no trae
    ningun `<a href="/trabajo/...">` en el HTML servido, solo ese
    payload.

    Para integrar este portal de forma confiable hay dos caminos:
    - Reimplementar el deserializador "devalue" de Nuxt para leer ese
      payload (fragil: formato interno no documentado, puede cambiar
      con cada deploy del sitio).
    - Usar un navegador headless (Selenium/Playwright) para esperar la
      hidratacion del cliente y leer el DOM ya renderizado.

    Se deja como stub para no fingir una integracion que en la
    practica siempre devuelve cero resultados de forma silenciosa.
    """

    portal = Portal.TRABAJANDO
    stub_reason = (
        "Trabajando.cl renderiza las ofertas client-side (Nuxt); el HTML inicial no "
        "trae datos parseables. Requiere deserializar su payload __NUXT_DATA__ o usar "
        "un navegador headless."
    )
