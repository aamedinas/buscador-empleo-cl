"""Heuristica de estimacion salarial y resumen ejecutivo.

No hay API publica de sueldos de mercado conectada; esto es una
aproximacion por palabras clave y promedios historicos declarados en
`SALARY_BANDS_CLP`, pensada como punto de partida. Ajustar las bandas
segun datos reales (ej. encuestas sectoriales) cuando se tengan.
"""

import re

from app.models.job import SalaryRange

# Rangos aproximados mensuales en CLP bruto, por nivel de cargo.
SALARY_BANDS_CLP: dict[str, tuple[int, int]] = {
    "gerente": (3_800_000, 7_500_000),
    "sub-gerente": (2_800_000, 5_000_000),
    "subgerente": (2_800_000, 5_000_000),
    "jefe": (2_200_000, 3_800_000),
    "lider": (1_900_000, 3_200_000),
    "líder": (1_900_000, 3_200_000),
    "coordinador": (1_600_000, 2_600_000),
    "analista": (1_100_000, 2_000_000),
}

_DEFAULT_BAND = (1_200_000, 2_200_000)

_EXPLICIT_SALARY_RE = re.compile(
    r"\$?\s?(\d{1,3}(?:[.,]\d{3})+)\s*(?:-|a|hasta)?\s*\$?\s?(\d{1,3}(?:[.,]\d{3})+)?",
)


def _parse_clp_number(raw: str) -> int:
    return int(raw.replace(".", "").replace(",", ""))


def estimate_salary_range(title: str, description: str | None = None) -> SalaryRange:
    """Intenta extraer un sueldo publicado explicitamente; si no hay,
    cae a la banda historica segun palabras clave del cargo."""

    text = description or ""
    match = _EXPLICIT_SALARY_RE.search(text)
    if match and match.group(1):
        low = _parse_clp_number(match.group(1))
        high = _parse_clp_number(match.group(2)) if match.group(2) else low
        if low >= 300_000:
            return SalaryRange(min_clp=min(low, high), max_clp=max(low, high), is_estimated=False, source="published")

    title_lower = title.lower()
    for keyword, (low, high) in SALARY_BANDS_CLP.items():
        if keyword in title_lower:
            return SalaryRange(min_clp=low, max_clp=high, is_estimated=True, source="historical_average")

    low, high = _DEFAULT_BAND
    return SalaryRange(min_clp=low, max_clp=high, is_estimated=True, source="historical_average")


def build_executive_summary(title: str, company: str, description: str | None = None) -> str:
    """Genera un resumen ejecutivo de 2 lineas a partir del titulo,
    empresa y (si existe) las primeras frases de la descripcion."""

    line_one = f"{title} en {company}."

    if description:
        clean = re.sub(r"\s+", " ", description).strip()
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        snippet = " ".join(sentences[:2])[:220].strip()
        line_two = snippet if snippet else "Sin descripcion detallada disponible en el portal de origen."
    else:
        line_two = "Sin descripcion detallada disponible en el portal de origen."

    return f"{line_one}\n{line_two}"
