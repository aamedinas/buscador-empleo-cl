"""CLI opcional: ejecuta una busqueda y muestra una tabla en consola,
sin pasar por la API HTTP ni por Keycloak (uso local/manual).

Uso:
    python cli.py --roles "Gerente" "Jefe de infraestructura" --csv salida.csv
"""

import argparse
import asyncio
import csv as csv_module
import sys

from app.core.logging import configure_logging
from app.models.job import JobSearchRequest
from app.scrapers.aggregator import search_all_portals


def _print_table(postings: list) -> None:
    if not postings:
        print("Sin resultados.")
        return

    headers = ["Portal", "Cargo", "Empresa", "Ubicacion", "Salario (CLP)", "URL"]
    rows = [
        [
            p.portal.value,
            p.title[:40],
            p.company[:25],
            p.location[:20],
            f"{p.salary_range.min_clp:,} - {p.salary_range.max_clp:,}".replace(",", ".")
            if p.salary_range.min_clp
            else "N/D",
            str(p.url),
        ]
        for p in postings
    ]

    widths = [max(len(str(row[i])) for row in ([headers] + rows)) for i in range(len(headers))]
    line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))


async def main() -> None:
    configure_logging("INFO")

    parser = argparse.ArgumentParser(description="Buscador de empleo CLI")
    parser.add_argument("--roles", nargs="+", default=None)
    parser.add_argument("--industries", nargs="+", default=None, help="Ej: Tecnologia Retail")
    parser.add_argument("--location", default=None)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--csv", default=None, help="Ruta de archivo CSV de salida (opcional)")
    args = parser.parse_args()

    request = JobSearchRequest(
        roles=args.roles or JobSearchRequest().roles,
        industries=args.industries,
        location=args.location,
        limit_per_portal=args.limit,
    )

    postings, portal_status = await search_all_portals(request)
    _print_table(postings)

    print()
    for status in portal_status:
        state = "OK" if status.ok else f"ERROR: {status.error}"
        print(f"{status.portal.value}: {status.count} resultados [{state}]")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv_module.writer(f)
            writer.writerow(["titulo", "empresa", "ubicacion", "portal", "resumen", "salario_min_clp", "salario_max_clp", "url"])
            for p in postings:
                writer.writerow(
                    [p.title, p.company, p.location, p.portal.value, p.summary.replace("\n", " | "), p.salary_range.min_clp, p.salary_range.max_clp, str(p.url)]
                )
        print(f"\nExportado a {args.csv}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
