import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _fast_test_settings():
    """Evita que los tests esperen los delays de politeness reales
    (1.5-4s por request) y desactiva Keycloak para los tests de API."""

    settings = get_settings()
    original = (
        settings.scraping_min_delay_seconds,
        settings.scraping_max_delay_seconds,
        settings.scraping_max_retries,
        settings.auth_enabled,
    )

    settings.scraping_min_delay_seconds = 0
    settings.scraping_max_delay_seconds = 0
    settings.scraping_max_retries = 1
    settings.auth_enabled = False

    yield

    (
        settings.scraping_min_delay_seconds,
        settings.scraping_max_delay_seconds,
        settings.scraping_max_retries,
        settings.auth_enabled,
    ) = original
