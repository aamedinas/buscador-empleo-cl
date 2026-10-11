# Arquitectura

Construido siguiendo el `MANIFIESTO DE DESARROLLO.md` de Arturo Medina:
FastAPI + Keycloak (OIDC) en el backend, Next.js en el frontend, Docker
y Traefik en infraestructura, logs JSON estructurados.

## Vista general

```
                         ┌─────────────────────┐
   Navegador  ──────────▶│  Frontend (Next.js) │
                         │  localhost:3000      │
                         └──────────┬───────────┘
                                    │ fetch + Bearer token (JWT)
                                    ▼
                         ┌─────────────────────┐
                         │  Backend (FastAPI)   │
                         │  /api/v1/jobs/*       │
                         └───┬──────────────┬───┘
                             │              │
                 valida JWT  │              │ persiste cache
                 (JWKS)      ▼              ▼
                     ┌───────────┐   ┌──────────────┐
                     │ Keycloak  │   │ Postgres/     │
                     │ (OIDC)    │   │ SQLite        │
                     └───────────┘   └──────────────┘
                             │
                             │ scraping (httpx + BeautifulSoup)
                             ▼
          ┌──────────────────────────────────────────────┐
          │ Computrabajo │ GetOnBrd │ Trabajando.com (stub)│
          │ Laborum (stub) │ LinkedIn (stub) │ Indeed (stub)│
          └──────────────────────────────────────────────┘
```

## Backend (`backend/app`)

| Capa | Responsabilidad |
|---|---|
| `api/v1/jobs.py` | Rutas HTTP: `POST /jobs/search`, `POST /jobs/search/csv`. Orquesta scraping + persistencia, no contiene logica de negocio propia. |
| `scrapers/` | Un modulo por portal (`BaseScraper` + subclases) y `aggregator.py`, que corre todas las combinaciones portal × cargo × rubro en paralelo (`asyncio.gather`) y deduplica resultados por URL. |
| `core/salary.py` | Heuristica de rango salarial (sueldo explicito en la descripcion, o banda historica por palabra clave) y generacion del resumen ejecutivo de 2 lineas. |
| `core/security.py` | Resource server OIDC: valida el JWT recibido contra el JWKS de Keycloak (RS256, audiencia, issuer). No emite tokens, no maneja login. |
| `core/config.py` | Settings centralizadas (Pydantic `BaseSettings`), leidas de variables de entorno / `.env`. |
| `core/logging.py` | Logging JSON estructurado (un objeto por linea, con `extra_fields` para contexto). |
| `db/` | SQLAlchemy async. `JobPostingRecord` cachea cada oferta vista (deduplicada por URL) para historico/export. |
| `models/job.py` | Esquemas Pydantic: `JobPosting`, `JobSearchRequest`, `JobSearchResponse`, `SalaryRange`, `Portal`. Es el contrato entre scrapers, API y frontend. |

### Por que un scraper por portal y no uno generico

Cada portal chileno tiene una estructura de HTML, URLs de busqueda y
(en el caso de Trabajando.com/Laborum) arquitectura frontend
completamente distintas — no hay un patron comun que valga la pena
abstraer mas alla de lo que ya hace `BaseScraper` (HTTP con
reintentos/backoff, delays de politeness, normalizacion a
`JobPosting`). Ver `docs/SCRAPING.md` para el detalle de que portal
funciona de verdad y por que.

### Cruce cargo × rubro

`JobSearchRequest.industries` es una lista opcional de rubros (texto
libre, ej. "Tecnologia"). El agregador genera una tarea de busqueda
por cada combinacion `(portal, cargo, rubro)` — si no se especifica
rubro, se busca solo por cargo. Los portales tratados son buscadores
de texto simple sin filtro estructurado por rubro, asi que el rubro se
suma como palabra clave extra a la query (`BaseScraper._build_query`).

Siglas ambiguas en español (como "TI", que tambien es el pronombre
"ti") se expanden a una frase sin ambiguedad antes de mandarlas al
buscador del portal, para no traer resultados de rubros no
relacionados (ver `BaseScraper._INDUSTRY_QUERY_EXPANSIONS`).

### Deduplicacion

Como una misma oferta puede aparecer en mas de una combinacion de
cargo/rubro buscada, `aggregator._dedupe_by_url` filtra los resultados
finales por URL antes de devolverlos. El conteo por portal
(`PortalResult.count`) si refleja el total crudo encontrado por ese
portal (no deduplicado), para no esconder cuanto trabajo hizo
realmente el scraper.

## Frontend (`frontend/src`)

| Carpeta | Responsabilidad |
|---|---|
| `app/` | Paginas (Next.js App Router). `page.tsx` es la unica pantalla: formulario + dashboard + resultados. `app/api/auth/[...nextauth]` es el endpoint de NextAuth. |
| `auth/auth.ts` | Configuracion de NextAuth con el provider de Keycloak (Authorization Code + PKCE, cliente publico). |
| `components/` | `SearchForm`, `ChipMultiSelect` (reusado para cargos y rubros), `DashboardStats` (graficos de barras), `JobCard`/`JobResultsList`, `AuthButton`, `PortalStatusBadges`. Sin logica de negocio: todos reciben datos ya normalizados por props. |
| `services/` | `api.ts` (fetch tipado al backend) y `types.ts` (espejo de los esquemas Pydantic del backend + listas de UI: cargos/rubros/ciudades por defecto). |

### Autenticacion

El cliente Keycloak `buscador-empleo-frontend` es publico (sin client
secret), por eso NextAuth se configura con
`token_endpoint_auth_method: "none"` y `checks: ["pkce", "state"]`
— ver comentario en `src/auth/auth.ts`. El access token se guarda en
la sesion JWT de NextAuth y se manda como `Authorization: Bearer` en
cada llamada a la API (`src/services/api.ts`).

Para que el backend acepte ese token, el cliente del frontend en
Keycloak tiene un `protocolMapper` tipo `oidc-audience-mapper` que
agrega `buscador-empleo-backend` al claim `aud` del access token (ver
`keycloak/realm-export.json`) — sin eso, el backend rechazaria el
token por audiencia invalida.

Con `NEXT_PUBLIC_AUTH_ENABLED=false` (y el backend con
`AUTH_ENABLED=false`), la UI omite el login y llama a la API sin
token — modo usado para desarrollo local sin tener que levantar
Keycloak.

### Dashboard de estadisticas

`DashboardStats` calcula las estadisticas (por rubro, por region, por
rango salarial) **en el cliente**, a partir de los resultados de la
ultima busqueda — no hay un endpoint de agregacion en el backend. Es
una decision de alcance: mas simple de mantener, pero las estadisticas
se resetean en cada busqueda nueva y no reflejan el historico
acumulado en la base de datos.
