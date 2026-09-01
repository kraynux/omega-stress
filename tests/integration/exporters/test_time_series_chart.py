from xml.etree import ElementTree

from omega_lib.theme.policies import EXPORT_PALETTES

from omega_stress.domain.runs.models import IntervalSample
from omega_stress.infrastructure.exporters.time_series_chart import (
    TimeSeriesLine,
    render_time_series_chart,
)

_PALETTE = EXPORT_PALETTES["omega-base"]


def _sample(at_second: float, *, observed: float) -> IntervalSample:
    return IntervalSample(
        at_second=at_second,
        observed_rate_per_minute=observed,
        p50_latency_ms=0.0,
        p95_latency_ms=0.0,
        p99_latency_ms=0.0,
        error_count=0,
        request_count=0,
    )


def test_empty_samples_produce_no_chart():
    svg = render_time_series_chart(
        [],
        series=(TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),),
        title="Debit",
        palette=_PALETTE,
    )

    assert svg == ""


def test_series_entirely_none_produces_no_chart():
    samples = [_sample(0.0, observed=10.0), _sample(1.0, observed=20.0)]

    svg = render_time_series_chart(
        samples,
        series=(TimeSeriesLine("Jamais mesure", _PALETTE.accent, lambda s: None),),
        title="Rien",
        palette=_PALETTE,
    )

    assert svg == ""


def test_valid_series_produces_parseable_svg_with_one_polyline_per_line():
    samples = [
        _sample(0.0, observed=10.0),
        _sample(1.0, observed=20.0),
        _sample(2.0, observed=15.0),
    ]

    svg = render_time_series_chart(
        samples,
        series=(
            TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),
            TimeSeriesLine("Demande", _PALETTE.secondary, lambda s: 15.0),
        ),
        title="Debit (requetes/min)",
        palette=_PALETTE,
    )

    assert svg.startswith("<svg")
    root = ElementTree.fromstring(svg)  # leve si le XML est invalide
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    assert len(polylines) == 2


def test_partial_series_are_omitted_individually():
    """Une serie dont AUCUN echantillon n'a de valeur est omise, mais le
    graphique reste trace pour les autres series exploitables."""
    samples = [_sample(0.0, observed=10.0), _sample(1.0, observed=20.0)]

    svg = render_time_series_chart(
        samples,
        series=(
            TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),
            TimeSeriesLine("Jamais mesure", _PALETTE.secondary, lambda s: None),
        ),
        title="Debit",
        palette=_PALETTE,
    )

    root = ElementTree.fromstring(svg)
    polylines = root.findall("{http://www.w3.org/2000/svg}polyline")
    assert len(polylines) == 1


def test_flat_series_does_not_divide_by_zero():
    samples = [_sample(0.0, observed=10.0), _sample(1.0, observed=10.0)]

    svg = render_time_series_chart(
        samples,
        series=(TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),),
        title="Debit",
        palette=_PALETTE,
    )

    assert svg  # aucune exception, un graphique est bien produit


def test_long_run_downsamples_the_polyline():
    # Mode "profil" D1-D6 (2026-09-01) : un profil `soak` (120 min) produit
    # jusqu'a ~7200 echantillons — le SVG doit rester borne plutot que de
    # tracer un point par echantillon.
    samples = [_sample(float(i), observed=float(i)) for i in range(1000)]

    svg = render_time_series_chart(
        samples,
        series=(TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),),
        title="Debit",
        palette=_PALETTE,
    )

    root = ElementTree.fromstring(svg)
    polyline = root.find("{http://www.w3.org/2000/svg}polyline")
    point_count = len(polyline.get("points").split())

    assert 0 < point_count <= 300
    assert point_count < len(samples)


def test_short_run_keeps_every_point():
    samples = [_sample(float(i), observed=float(i)) for i in range(10)]

    svg = render_time_series_chart(
        samples,
        series=(TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),),
        title="Debit",
        palette=_PALETTE,
    )

    root = ElementTree.fromstring(svg)
    polyline = root.find("{http://www.w3.org/2000/svg}polyline")
    point_count = len(polyline.get("points").split())

    assert point_count == len(samples)


def test_title_is_escaped_against_xml_injection():
    samples = [_sample(0.0, observed=10.0)]
    malicious_title = "</svg><script>alert(1)</script>"

    svg = render_time_series_chart(
        samples,
        series=(TimeSeriesLine("Reel", _PALETTE.accent, lambda s: s.observed_rate_per_minute),),
        title=malicious_title,
        palette=_PALETTE,
    )

    assert "<script>" not in svg
    ElementTree.fromstring(svg)  # reste un document XML unique et valide
