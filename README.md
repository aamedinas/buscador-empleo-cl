# Buscador de Empleo Chile

API que consulta multiples portales de empleo chilenos para los cargos
Sub-gerente, Lider de produccion, Jefe de infraestructura y Gerente, y
entrega por oferta: resumen ejecutivo de 2 lineas, rango salarial
estimado y URL directa de postulacion.

Construido siguiendo el `MANIFIESTO DE DESARROLLO.md` (FastAPI, Keycloak
OIDC, Docker, Postgres, Traefik, logs JSON, rutas `/api/v1`).

## Aviso importante sobre scraping

Estado verificado contra el HTML real de cada portal el 2026-10-10
(busqueda "gerente"), no solo escrito a ciegas:

- **Computrabajo y GetOnBrd**: scraping real funcionando (`httpx` +
  BeautifulSoup), con delays entre requests, reintentos acotados y
  manejo de bloqueos (HTTP 403/429). Los selectores (`SELECTORS` en
  cada modulo) fueron probados contra una descarga real de cada sitio
  y devuelven titulo/empresa/ubicacion correctos. Aun asi son un
  snapshot a esa fecha: **revisalos si los resultados empiezan a venir
  vacios o incorrectos**, porque cualquier rediseno del sitio los
  rompe.
- **Trabajando.com y Laborum**: quedan como **stub** (devuelven lista
  vacia), igual que LinkedIn/Indeed, porque **no son sitios con HTML
  estatico**: son SPAs (Nuxt y React respectivamente) cuyo HTML inicial
  no trae las ofertas como elementos parseables con BeautifulSoup.
  Trabajando.cl las trae en un payload interno serializado
  (`__NUXT_DATA__`, formato "devalue" de Nuxt, no JSON plano); Laborum
  no trae ningun dato en el HTML inicial. Integrarlos de verdad
  requeriria reimplementar ese deserializador (fragil, formato interno
  no documentado) o un navegador headless (Selenium/Playwright) que
  espere la hidratacion del cliente — fuera del alcance de esta
  version. El detalle de cada caso esta en el docstring de
  `trabajando.py` y `laborum.py`.
- **LinkedIn Jobs e Indeed Chile**: quedan como **stub** (`linkedin.py`,
  `indeed.py`) por una razon distinta: ambos prohiben explicitamente el
  scraping automatizado en sus Terminos de Servicio y usan deteccion
  anti-bot activa; LinkedIn ademas tiene antecedentes de acciones
  legales contra scrapers.
- En todos los casos stub, la interfaz (`BaseScraper`) ya esta lista
  para conectar, cuando corresponda, una API oficial, un navegador
  headless o un proveedor de datos con licencia, sin tener que tocar
  el resto de la aplicacion.
- Revisa y respeta siempre `robots.txt` y los ToS de cada sitio antes
  de usar esto en un entorno productivo o con volumen alto de
  requests.

## Arquitectura

```
backend/
  app/
    api/v1/        # rutas FastAPI (/api/v1/jobs/search, /search/csv)
    core/          # config, logging JSON, seguridad (JWKS/Keycloak), heuristica salarial
    models/        # esquemas Pydantic (JobPosting, JobSearchRequest, ...)
    db/            # SQLAlchemy async (cache de resultados en Postgres)
    scrapers/      # un modulo por portal + agregador que corre todo en paralelo
  tests/           # pytest (heuristica salarial, scrapers con respx, API)
  cli.py           # modo consola, sin pasar por Keycloak
frontend/
  src/
    app/           # paginas (App Router) y ruta de NextAuth (/api/auth/[...nextauth])
    components/    # SearchForm, JobCard, JobResultsList, AuthButton, ...
    services/      # cliente de la API del backend (fetch + tipos)
    auth/          # configuracion de NextAuth (Keycloak, PKCE)
keycloak/
  realm-export.json  # realm, clientes (backend bearer-only + frontend PKCE) y rol job_searcher
docker-compose.yml  # backend + frontend + postgres + keycloak + traefik
.github/workflows/ci.yml  # lint + tests + build de imagen
```

## Desarrollo local (sin Docker)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt
copy .env.example .env    # y editar AUTH_ENABLED=false para probar sin Keycloak

uvicorn app.main:app --reload
```

Con `AUTH_ENABLED=false`, la API no exige token y usa un usuario de
desarrollo (`get_current_user` en `app/core/security.py`).

Documentacion OpenAPI automatica en `http://localhost:8000/docs`.

## Con Docker Compose (stack completo con Keycloak)

```bash
docker compose up --build
```

Esto levanta Traefik, Postgres, Keycloak (con el realm `buscador-empleo`
pre-cargado desde `keycloak/realm-export.json`, usuario `arturo` /
password temporal `changeme`), el backend y el frontend. La API queda
detras de Traefik en `/api` y `/health`; el frontend en `/` (puerto
3000 expuesto directo tambien). Antes de levantar el stack, copia
`backend/.env.example` a `backend/.env` y `frontend/.env.local.example`
a `frontend/.env.local` (con un `NEXTAUTH_SECRET` real).

Para obtener un token de prueba (flujo Authorization Code + PKCE lo
ejecuta normalmente el frontend; para pruebas manuales via Postman/
curl puede usarse el flujo de password del usuario de desarrollo
expuesto por Keycloak en modo `start-dev`).

## Frontend (Next.js)

Interfaz profesional para buscar, ver y exportar las ofertas sin pasar
por `/docs`. Usa NextAuth con Keycloak (Authorization Code + PKCE,
cliente publico `buscador-empleo-frontend`) y llama directo a la API
del backend desde el navegador.

```bash
cd frontend
npm install
copy .env.local.example .env.local   # editar NEXTAUTH_SECRET con uno real:
                                      # openssl rand -base64 32
npm run dev
```

Abre `http://localhost:3000`. Con `NEXT_PUBLIC_AUTH_ENABLED=false` en
`.env.local` (modo desarrollo) la UI omite el login y llama a la API
sin token — util para probar sin tener Keycloak corriendo, siempre que
el backend tambien tenga `AUTH_ENABLED=false`. Con ambos en `true`
(valor por defecto), hace falta el stack completo de `docker compose up`
para iniciar sesion de verdad.

Verificado en esta maquina: `npm run typecheck`, `npm run lint` y
`npm run build` pasan sin errores, y el HTML servido por `next dev`
se probo con el backend real (CORS preflight entre `localhost:3000` y
`localhost:8000` responde `200`). **No se pudo verificar visualmente en
un navegador real** (sin herramienta de navegador disponible en este
entorno) ni el flujo de login contra un Keycloak real corriendo — eso
queda pendiente de que levantes `docker compose up` y pruebes el click
de "Iniciar sesion" tu mismo.

### Nota de seguridad de dependencias (`npm audit`)

Al instalar, `npm audit` reporta vulnerabilidades. Se resolvieron las
mas relevantes sin cambios grandes:

- `next-auth` se subio a `4.24.15` (de `4.24.8`): corrige fallas
  criticas/altas de Auth.js (bypass de homografos en Email provider,
  excepcion no capturada en `getToken()`, cookies de PKCE/state no
  atadas al provider).
- `tailwindcss`/`postcss` se subieron a sus ultimos parches `3.x`/`8.x`.

Quedan sin resolver varias vulnerabilidades (algunas criticas) del
**paquete `next` en si** (DoS, SSRF, XSS, RCE en casos especificos):
solo las corrige el salto a `next@16`, que es una migracion mayor y sin
soporte confirmado de `next-auth` v4 (la v5 sigue en beta). No se hizo
ese salto a ciegas en esta pasada porque:

- No se usa `next/image` (el vector de la RCE de AVIF no aplica).
- No hay Server Actions ni servidor custom (varios DoS/SSRF listados
  solo aplican a esos casos).
- El deploy objetivo es el Dockerfile sobre Linux (`node:20-alpine`),
  no un host Windows directo (el RCE "windows-hosted" no aplica aqui).

Aun asi, es deuda tecnica real: antes de exponer esto a internet sin
Keycloak de por medio, conviene evaluar migrar a `next@16` + Auth.js v5
cuando esta ultima salga de beta, o correr `npm audit` de nuevo
periodicamente.

## Endpoints

- `POST /api/v1/jobs/search` — body `JobSearchRequest` (roles, portals,
  location, limit_per_portal opcional) -> `JobSearchResponse` (lista de
  ofertas + estado por portal).
- `POST /api/v1/jobs/search/csv` — mismo body, devuelve un CSV
  descargable.
- `GET /health` — healthcheck.

## CLI

```bash
cd backend
python cli.py --roles "Gerente" "Jefe de infraestructura" --csv salida.csv
```

Corre el scraping directo (sin HTTP, sin Keycloak) y muestra una tabla
en consola; `--csv` exporta los resultados.

## Tests

```bash
cd backend
pytest -v
```

Incluye tests de la heuristica de salario/resumen, de los scrapers
(HTML simulado con `respx`, sin golpear los sitios reales) y de la API
con los scrapers mockeados.

## Rango salarial y resumen ejecutivo

`app/core/salary.py` primero busca un sueldo publicado explicitamente
en la descripcion de la oferta; si no encuentra uno, usa una banda
historica aproximada por palabra clave del cargo (`SALARY_BANDS_CLP`).
Son aproximaciones de partida, no datos de mercado verificados: ajustar
las bandas si se cuenta con informacion mas precisa.
