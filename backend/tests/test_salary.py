from app.core.salary import build_executive_summary, estimate_salary_range


def test_estimate_salary_range_published_in_description():
    result = estimate_salary_range("Analista", "Renta liquida $1.500.000 - $1.800.000 mensual")
    assert result.is_estimated is False
    assert result.source == "published"
    assert result.min_clp == 1_500_000
    assert result.max_clp == 1_800_000


def test_estimate_salary_range_falls_back_to_keyword_band():
    result = estimate_salary_range("Gerente de Operaciones", description=None)
    assert result.is_estimated is True
    assert result.source == "historical_average"
    assert result.min_clp == 3_800_000


def test_estimate_salary_range_unknown_title_uses_default_band():
    result = estimate_salary_range("Pasante de verano", description=None)
    assert result.is_estimated is True
    assert result.min_clp == 1_200_000


def test_build_executive_summary_has_two_lines():
    summary = build_executive_summary(
        "Jefe de Infraestructura",
        "Acme SpA",
        "Buscamos liderar el area de TI. Se requiere experiencia en cloud. Otros requisitos.",
    )
    lines = summary.split("\n")
    assert len(lines) == 2
    assert "Jefe de Infraestructura" in lines[0]
    assert "Acme SpA" in lines[0]


def test_build_executive_summary_without_description():
    summary = build_executive_summary("Gerente", "Empresa X", None)
    assert "Sin descripcion detallada" in summary
