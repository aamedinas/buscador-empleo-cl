# Buscador de Empleo Chile

Aplicacion que busca ofertas laborales en portales chilenos, cruzando
cargo, rubro y ciudad, y entrega por oferta: resumen ejecutivo de 2
lineas, rango salarial estimado y URL directa de postulacion. Incluye
un dashboard con estadisticas (por rubro, region y rango salarial)
sobre los resultados de cada busqueda.

Construido siguiendo el `MANIFIESTO DE DESARROLLO.md` de Arturo Medina
(FastAPI, Keycloak OIDC, Next.js, Docker, Postgres, Traefik, logs
JSON, rutas `/api/v1`).

## Documentacion

| Doc | Contenido |
|---|---|
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Como esta armado el backend y el frontend, y por que |
| [docs/API.md](docs/API.md) | Referencia de endpoints con ejemplos de request/response |
| [docs/SCRAPING.md](docs/SCRAPING.md) | Que portal funciona de verdad, cual es stub y por que |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Como correrlo (local y Docker) + variables de entorno |

## Quick start

**Local sin Docker** (mas rapido para desarrollar):

```bash
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env    # editar AUTH_ENABLED=false para probar sin Keycloak
uvicorn app.main:app --reload
```

```bash
cd frontend && npm install
copy .env.local.example .env.local   # NEXT_PUBLIC_AUTH_ENABLED=false para combinar con el backend
npm run dev
```

Abre `http://localhost:3000` (UI) y `http://localhost:8000/docs`
(OpenAPI interactivo). Detalle completo de variables de entorno en
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

**Stack completo con Docker** (Traefik + Postgres + Keycloak + backend
+ frontend):

```bash
docker compose up --build
```

Ver [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) para la configuracion
previa necesaria (`.env` / `.env.local`) y que falta por verificar de
este modo (nunca se corrio de punta a punta en esta version).

## Estado de los portales (resumen)

| Portal | Estado |
|---|---|
| Computrabajo, GetOnBrd | ✅ Scraping real, verificado contra HTML en vivo |
| Trabajando.com, Laborum | ⛔ Stub (son SPAs sin datos accesibles por HTML) |
| LinkedIn, Indeed Chile | ⛔ Stub (ToS prohibe scraping + anti-bot) |

Detalle completo, selectores verificados y como conectar una
integracion real para los stubs: [docs/SCRAPING.md](docs/SCRAPING.md).

## CLI

```bash
cd backend
python cli.py --roles "Gerente" "Jefe de infraestructura" --industries "Tecnologia" --csv salida.csv
```

Corre el scraping directo (sin HTTP, sin Keycloak) y muestra una tabla
en consola; `--csv` exporta los resultados.

## Tests

```bash
cd backend
pytest -v
```

19 tests: heuristica de salario/resumen, scrapers (HTML simulado con
`respx`, sin golpear los sitios reales), cruce rol×rubro y
deduplicacion en el agregador, y API con los scrapers mockeados.

## Nota de seguridad de dependencias del frontend

`next-auth` se subio a `4.24.15` (corrige fallas criticas/altas de
Auth.js). Quedan vulnerabilidades sin resolver en el paquete `next` en
si, que solo corrige el salto a `next@16` (incompatibilidad no
confirmada con `next-auth` v4 estable); el detalle de por que no se
hizo ese salto a ciegas y que mitigaciones ya aplican esta en
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
