# Referencia de la API

Documentacion interactiva (OpenAPI/Swagger) siempre disponible en
`http://localhost:8000/docs` con el backend corriendo — esta pagina es
un complemento estatico con ejemplos, no un sustituto.

Prefijo de todas las rutas: `/api/v1`. Autenticacion: `Authorization:
Bearer <access_token>` (JWT de Keycloak), salvo que el backend corra
con `AUTH_ENABLED=false` (modo desarrollo).

## `POST /jobs/search`

Busca ofertas cruzando cargos × rubros (si se dan) en los portales
indicados, y devuelve los resultados deduplicados por URL.

### Body (`JobSearchRequest`)

| Campo | Tipo | Default | Descripcion |
|---|---|---|---|
| `roles` | `string[]` | Sub-gerente, Lider de produccion, Jefe de infraestructura, Gerente | Cargos a buscar |
| `portals` | `Portal[] \| null` | `null` (todos) | `trabajando.com`, `laborum`, `computrabajo`, `getonbrd`, `linkedin`, `indeed_cl` |
| `industries` | `string[] \| null` | `null` (sin filtro) | Rubros en texto libre, ej. `["Tecnologia"]`. Si se dan varios, se cruzan con cada cargo |
| `location` | `string \| null` | `null` | Filtro de texto contra la ubicacion publicada (ej. `"Santiago"`) |
| `limit_per_portal` | `int` | `20` | Maximo de resultados por combinacion portal×cargo×rubro (1-100) |

### Ejemplo

```bash
curl -X POST http://localhost:8000/api/v1/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["Gerente", "Jefe de infraestructura"],
    "industries": ["Tecnologia"],
    "portals": ["computrabajo", "getonbrd"],
    "location": "Santiago",
    "limit_per_portal": 10
  }'
```

### Respuesta (`JobSearchResponse`)

```json
{
  "total": 12,
  "results": [
    {
      "title": "Gerente de Tecnologia",
      "company": "Empresa Demo SpA",
      "location": "Santiago - Providencia, R.Metropolitana",
      "portal": "computrabajo",
      "url": "https://www.computrabajo.cl/ofertas-de-trabajo/...",
      "published_at": null,
      "summary": "Gerente de Tecnologia en Empresa Demo SpA.\nLidera el area de TI...",
      "salary_range": {
        "min_clp": 2200000,
        "max_clp": 3800000,
        "is_estimated": true,
        "source": "historical_average"
      },
      "industry": "Tecnologia"
    }
  ],
  "portal_status": [
    { "portal": "computrabajo", "ok": true, "count": 7, "error": null },
    { "portal": "getonbrd", "ok": true, "count": 5, "error": null }
  ]
}
```

Notas:
- `total`/`results` ya vienen deduplicados por URL.
- `portal_status[].count` es el total **crudo** encontrado por ese
  portal (antes de deduplicar), para diagnosticar si un portal esta
  respondiendo bien.
- `salary_range.source` es `"published"` si se extrajo un sueldo
  explicito de la descripcion, o `"historical_average"` si es una
  banda estimada por palabra clave del cargo (ver
  `docs/ARQUITECTURA.md`).
- `industry` en cada resultado es el rubro de busqueda que encontro
  esa oferta (`null` si no se filtro por rubro) — no es una
  clasificacion verificada de la oferta en si.

## `POST /jobs/search/csv`

Mismo body que `/jobs/search`. Devuelve un CSV descargable
(`Content-Disposition: attachment`) con columnas: `titulo`, `empresa`,
`ubicacion`, `portal`, `rubro`, `resumen`, `salario_min_clp`,
`salario_max_clp`, `url`, `fecha_publicacion`.

## `GET /health`

Sin autenticacion. `{"status": "ok"}` si el servicio esta arriba.
