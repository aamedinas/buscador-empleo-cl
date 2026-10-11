from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "buscador-empleo-cl"
    api_prefix: str = "/api/v1"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # CORS
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Keycloak / OIDC
    auth_enabled: bool = Field(default=True)
    keycloak_server_url: str = Field(default="http://keycloak:8080")
    keycloak_realm: str = Field(default="buscador-empleo")
    keycloak_client_id: str = Field(default="buscador-empleo-backend")
    keycloak_jwks_cache_ttl_seconds: int = Field(default=3600)

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak_server_url}/realms/{self.keycloak_realm}"

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/certs"

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/buscador_empleo"
    )

    # Scraping
    scraping_min_delay_seconds: float = Field(default=1.5)
    scraping_max_delay_seconds: float = Field(default=4.0)
    scraping_request_timeout_seconds: float = Field(default=10.0)
    scraping_max_retries: int = Field(default=2)
    scraping_user_agents: list[str] = Field(
        default_factory=lambda: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
