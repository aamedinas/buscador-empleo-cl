# Estado del scraping por portal

Estado verificado contra el HTML real de cada portal el 2026-10-10
(busqueda "gerente" / "gerente tecnologia"), no solo escrito a ciegas.
Cada scraper vive en `backend/app/scrapers/<portal>.py`.

## Resumen

| Portal | Estado | Por que |
|---|---|---|
| Computrabajo | ✅ Scraping real | HTML estatico, selectores verificados |
| GetOnBrd | ✅ Scraping real | Server-rendered (Rails/Turbo), selectores verificados |
| Trabajando.com | ⛔ Stub | SPA (Nuxt): ofertas en payload `__NUXT_DATA__`, no HTML parseable |
| Laborum | ⛔ Stub | SPA (React): sin datos en el HTML inicial |
| LinkedIn Jobs | ⛔ Stub | ToS prohibe scraping + anti-bot activo |
| Indeed Chile | ⛔ Stub | ToS prohibe scraping + anti-bot activo |

## Computrabajo y GetOnBrd (scraping real)

`httpx` + BeautifulSoup, con:
- delays aleatorios entre requests (politeness, no evasion — ver
  `BaseScraper._polite_delay`)
- reintentos acotados con backoff en timeout/403/429
- `response.encoding` forzado a UTF-8 (httpx adivinaba mal el charset
  de estos sitios y producia mojibake en texto con tildes)

Los selectores CSS (diccionario `SELECTORS` en cada modulo) son un
**snapshot** a la fecha de verificacion. Revisarlos si los resultados
empiezan a venir vacios, con campos vacios, o con ubicacion/empresa
cruzadas — cualquier rediseno del sitio los rompe. El bug mas sutil
encontrado durante la verificacion: en Computrabajo, cuando una
empresa tiene rating, el badge del rating (`span.mr10`) queda *dentro*
del mismo parrafo que el nombre de la empresa, con la misma clase que
usa el parrafo de ubicacion — hubo que afinar el selector con
`:not(.dFlex)` para no confundir el rating con la ciudad.

## Trabajando.com y Laborum (stub)

No son sitios con HTML estatico:

- **Trabajando.com** es una SPA Nuxt. El HTML inicial no tiene ningun
  `<a href="/trabajo/...">` — las ofertas viven en un payload interno
  (`__NUXT_DATA__`) serializado en el formato "devalue" de Nuxt
  (referencias por indice a un array plano, no JSON convencional).
- **Laborum** es una SPA React (`id="root"`) sin ningun dato
  embebido — el listado se pide client-side despues de hidratar.

Integrarlos de verdad requeriria reimplementar el deserializador de
Nuxt (fragil, formato interno no documentado, puede cambiar con cada
deploy del sitio) o un navegador headless (Selenium/Playwright) que
espere la hidratacion del cliente antes de leer el DOM — ninguna de
las dos se hizo en esta version por el costo/fragilidad que implican
frente al resto del alcance.

## LinkedIn Jobs e Indeed Chile (stub)

Ambos prohiben explicitamente el scraping automatizado en sus
Terminos de Servicio y usan deteccion anti-bot activa; LinkedIn
ademas tiene antecedentes de acciones legales contra scrapers. Por eso
quedan como stub por decision deliberada, no por limitacion tecnica.

Rutas legitimas para integrarlos cuando corresponda:
- LinkedIn Talent Solutions / Jobs API (requiere partnership aprobado)
- Indeed Publisher / XML Feed program (requiere aprobacion)
- Un proveedor de datos de empleo con licencia

## Interfaz comun para conectar una integracion real

Todos los stubs (`StubScraper` en `base.py`) implementan la misma
interfaz `BaseScraper.search()` que los scrapers reales. El dia que
se conecte una API oficial, un navegador headless, o un proveedor de
datos para alguno de estos portales, solo hay que reemplazar el
cuerpo de `search()` en ese modulo — el resto de la aplicacion
(agregador, API, frontend) no necesita cambios.

## Cruce con rubro: cuidado con siglas ambiguas

Al combinar cargo + rubro en una sola query de texto libre (ver
`docs/ARQUITECTURA.md`), siglas de 2-3 letras pueden coincidir con
palabras comunes del español y traer ruido. Ejemplo real encontrado:
buscar rubro "TI" devolvia avisos de gastronomia/retail, porque "ti"
tambien es el pronombre ("trabaja para ti"). Se corrigio expandiendo
esas siglas a una frase sin ambiguedad antes de mandarlas al buscador
(`BaseScraper._INDUSTRY_QUERY_EXPANSIONS`). Si se agregan mas rubros
por sigla al frontend, revisar si necesitan la misma expansion.
