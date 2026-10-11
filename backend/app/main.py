from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import init_db

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicacion", extra={"extra_fields": {"env": settings.environment}})
    await init_db()
    yield
    logger.info("Deteniendo aplicacion")


app = FastAPI(
    title="Buscador de Empleo Chile",
    description=(
        "API que consulta multiples portales de empleo chilenos y entrega "
        "resumen ejecutivo, rango salarial estimado y URL de postulacion."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
