from app.models.job import Portal
from app.scrapers.base import StubScraper


class LinkedInScraper(StubScraper):
    """LinkedIn Jobs: su ToS prohibe expresamente el scraping automatizado
    (User Agreement, seccion "Dos and Don'ts") y usa deteccion anti-bot
    activa, con antecedentes de acciones legales contra scrapers.

    Para integrar LinkedIn de forma legitima:
    - LinkedIn Talent Solutions / Jobs API (requiere partnership aprobado), o
    - un agregador de datos con licencia (ej. proveedores de job feeds), o
    - que el propio usuario exporte/comparta manualmente las vacantes de interes.

    Esta clase mantiene la interfaz de BaseScraper para que, el dia que
    exista una de esas integraciones autorizadas, solo haya que
    reemplazar el cuerpo de `search()`.
    """

    portal = Portal.LINKEDIN
    stub_reason = (
        "LinkedIn prohibe scraping en su ToS y tiene anti-bot activo. "
        "Conectar via LinkedIn Talent Solutions API o un proveedor de datos licenciado."
    )
