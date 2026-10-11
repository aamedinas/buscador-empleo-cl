from app.models.job import Portal
from app.scrapers.base import StubScraper


class IndeedScraper(StubScraper):
    """Indeed Chile prohibe scraping en sus Terminos de Servicio y aplica
    bloqueo/challenges anti-bot de forma agresiva.

    Para integrar Indeed de forma legitima:
    - Indeed Publisher/XML Feed program (requiere aprobacion), o
    - un agregador de datos con licencia.

    Interfaz mantenida compatible con BaseScraper para conectar una
    integracion autorizada sin cambiar el resto de la aplicacion.
    """

    portal = Portal.INDEED
    stub_reason = (
        "Indeed prohibe scraping en su ToS y tiene anti-bot activo. "
        "Conectar via Indeed Publisher/XML Feed program o un proveedor de datos licenciado."
    )
