"""Validacion de JWT emitidos por Keycloak (OIDC, RS256) via JWKS.

El flujo de login (Authorization Code + PKCE) lo ejecuta el cliente
(frontend o herramienta externa) contra Keycloak. Este backend solo
actua como resource server: recibe el access_token en el header
Authorization y valida su firma/claims contra el JWKS del realm.
"""

import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict[str, Any] = {"keys": None, "fetched_at": 0.0}


async def _get_jwks() -> dict[str, Any]:
    settings = get_settings()
    now = time.time()
    if (
        _jwks_cache["keys"] is not None
        and now - _jwks_cache["fetched_at"] < settings.keycloak_jwks_cache_ttl_seconds
    ):
        return _jwks_cache["keys"]

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(settings.keycloak_jwks_url)
        response.raise_for_status()
        jwks = response.json()

    _jwks_cache["keys"] = jwks
    _jwks_cache["fetched_at"] = now
    return jwks


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    settings = get_settings()

    if not settings.auth_enabled:
        return {"sub": "dev-user", "preferred_username": "dev", "realm_access": {"roles": []}}

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta token de autenticacion",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        jwks = await _get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        key = next(
            (k for k in jwks["keys"] if k["kid"] == unverified_header.get("kid")),
            None,
        )
        if key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clave de firma desconocida (kid no encontrado en JWKS)",
            )

        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
            issuer=settings.keycloak_issuer,
            options={"verify_at_hash": False},
        )
        return claims
    except JWTError as exc:
        logger.warning("Token invalido", extra={"extra_fields": {"error": str(exc)}})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
