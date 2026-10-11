# Despliegue y variables de entorno

## Local, sin Docker (desarrollo rapido)

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt
copy .env.example .env          # editar AUTH_ENABLED=false para probar sin Keycloak
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
copy .env.local.example .env.local   # NEXT_PUBLIC_AUTH_ENABLED=false para que combine con el backend
npm run dev
```

Con ambos en modo desarrollo (`AUTH_ENABLED=false` /
`NEXT_PUBLIC_AUTH_ENABLED=false`) no se necesita Keycloak corriendo
para probar la busqueda.

## Stack completo con Docker Compose

```bash
docker compose up --build
```

Antes de correrlo:
1. `copy backend\.env.example backend\.env`
2. `copy frontend\.env.local.example frontend\.env.local` y generar un
   `NEXTAUTH_SECRET` real (`openssl rand -base64 32`, o cualquier
   string aleatorio largo — no uses el valor de ejemplo en nada que no
   sea tu maquina local).

Servicios que levanta: `traefik`, `postgres`, `keycloak` (con el
realm `buscador-empleo` pre-cargado desde
`keycloak/realm-export.json`), `backend`, `frontend`.

- Frontend: `http://localhost:3000` (y detras de Traefik en `/`)
- Backend: `http://localhost:8000` (y detras de Traefik en `/api`,
  `/health`)
- Keycloak admin console: `http://localhost:8081` (usuario
  `admin`/`admin`, solo para desarrollo local — cambiar en cualquier
  despliegue real)
- Usuario de prueba precargado en el realm: `arturo` / password
  temporal `changeme` (fuerza cambio de contraseña al primer login)

## Variables de entorno — backend (`backend/.env`)

| Variable | Default | Notas |
|---|---|---|
| `AUTH_ENABLED` | `true` | `false` omite la validacion JWT (solo desarrollo) |
| `KEYCLOAK_SERVER_URL` | `http://keycloak:8080` | Host interno dentro de docker-compose |
| `KEYCLOAK_REALM` | `buscador-empleo` | |
| `KEYCLOAK_CLIENT_ID` | `buscador-empleo-backend` | Debe coincidir con la audiencia (`aud`) del token |
| `DATABASE_URL` | `postgresql+asyncpg://...` | `sqlite+aiosqlite:///./dev.db` funciona para pruebas locales sin Postgres |
| `CORS_ALLOWED_ORIGINS` | `["http://localhost:3000"]` | Debe incluir el origen real del frontend |
| `SCRAPING_MIN_DELAY_SECONDS` / `SCRAPING_MAX_DELAY_SECONDS` | `1.5` / `4.0` | Delay de politeness entre requests a cada portal |

## Variables de entorno — frontend (`frontend/.env.local`)

| Variable | Default | Notas |
|---|---|---|
| `NEXTAUTH_URL` | `http://localhost:3000` | Debe coincidir con donde corre el frontend |
| `NEXTAUTH_SECRET` | — | **Generar uno real**, nunca usar el de ejemplo fuera de tu maquina |
| `KEYCLOAK_ISSUER` | `http://localhost:8081/realms/buscador-empleo` | |
| `KEYCLOAK_CLIENT_ID` | `buscador-empleo-frontend` | Cliente publico (sin secret) |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Debe ser alcanzable desde el navegador del usuario, no solo desde el contenedor |
| `NEXT_PUBLIC_AUTH_ENABLED` | `true` | `false` omite el login (debe combinar con `AUTH_ENABLED=false` en el backend) |

## Seguridad de dependencias del frontend (`npm audit`)

Al instalar, `npm audit` reporta vulnerabilidades. Se resolvieron las
mas relevantes sin cambios grandes:

- `next-auth` se subio a `4.24.15` (de `4.24.8`): corrige fallas
  criticas/altas de Auth.js (bypass de homografos en Email provider,
  excepcion no capturada en `getToken()`, cookies de PKCE/state no
  atadas al provider).
- `tailwindcss`/`postcss` se subieron a sus ultimos parches `3.x`/`8.x`.

Quedan sin resolver varias vulnerabilidades (algunas criticas) del
**paquete `next` en si** (DoS, SSRF, XSS, RCE en casos especificos):
solo las corrige el salto a `next@16`, que es una migracion mayor y
sin soporte confirmado de `next-auth` v4 (la v5 sigue en beta). No se
hizo ese salto a ciegas en esta pasada porque:

- No se usa `next/image` (el vector de la RCE de AVIF no aplica).
- No hay Server Actions ni servidor custom (varios DoS/SSRF listados
  solo aplican a esos casos).
- El deploy objetivo es el Dockerfile sobre Linux (`node:20-alpine`),
  no un host Windows directo (el RCE "windows-hosted" no aplica aqui).

Aun asi, es deuda tecnica real: antes de exponer esto a internet sin
Keycloak de por medio, conviene evaluar migrar a `next@16` + Auth.js
v5 cuando esta ultima salga de beta, o correr `npm audit` de nuevo
periodicamente.

## Lo que falta validar antes de un despliegue real

Ninguno de estos tres puntos se verifico contra una instancia real en
esta version (ver tambien `docs/SCRAPING.md` para los limites de los
scrapers):

1. **El stack completo de Docker** (`docker compose up`) nunca se
   corrio de punta a punta — no se confirmo que Traefik, Postgres,
   Keycloak y el backend/frontend se conecten correctamente entre
   contenedores.
2. **Login real contra Keycloak** — el realm y el mapper de audiencia
   estan escritos pero nunca se obtuvo un token real desde el
   frontend contra un Keycloak corriendo.
3. **CI** (`.github/workflows/ci.yml`) nunca se corrio en un runner de
   GitHub Actions real, solo se verificaron localmente los mismos
   comandos que ejecuta (`ruff`, `pytest`, `docker build`).
