# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Rendu d'un graphique SVG en ligne (serie temporelle) pour l'export HTML
— meme technique que `family_chart.py` d'omega-fold (D-009, portee ici
pour des series temporelles plutot qu'un histogramme) : mise en page
calculee ici en Python, aucune dependance de charting lourde.

N'importe PAS jinja2 (voir html_exporter.py, seul module autorise a le
faire) : construit une chaine `<svg>...</svg>` complete et autonome,
directement embarquee par le template via `| safe`. Les labels
proviennent d'un vocabulaire interne ferme (voir html_exporter.py, seul
appelant), jamais d'une entree utilisateur — `xml.sax.saxutils.escape`
est tout de meme applique par prudence (meme discipline que
family_chart.py)."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from math import ceil
from xml.sax.saxutils import escape

from omega_lib.theme.policies import Palette

from omega_stress.domain.runs.models import IntervalSample

_CHART_WIDTH = 640
_CHART_HEIGHT = 220
_MARGIN_LEFT = 55
_MARGIN_RIGHT = 20
_MARGIN_TOP = 34
_MARGIN_BOTTOM = 30
_Y_TICKS = 4
_MAX_CHART_POINTS = 300


@dataclass(frozen=True, slots=True)
class TimeSeriesLine:
    """Une serie a tracer sur le graphique : nom affiche dans la legende,
    couleur (une valeur de Palette deja resolue par l'appelant, jamais
    devinee ici), et accesseur pur qui extrait une valeur (ou None si non
    mesurable pour cet echantillon) d'un IntervalSample."""

    label: str
    color: str
    value: Callable[[IntervalSample], float | None]


def render_time_series_chart(
    samples: Sequence[IntervalSample],
    *,
    series: Sequence[TimeSeriesLine],
    title: str,
    palette: Palette,
) -> str:
    """Construit un graphique en ligne (une polyline par serie) sur l'axe
    temporel IntervalSample.at_second. Une serie dont aucun echantillon
    n'a de valeur exploitable (ex. SystemSnapshot jamais mesure) est
    simplement omise du graphique, jamais une ligne a zero trompeuse.
    Retourne une chaine vide si aucune serie n'a la moindre valeur — pas
    de graphique vide a afficher (meme convention que family_chart.py
    pour une liste vide)."""
    lines_with_points = [
        (line, points)
        for line in series
        if (points := _points(samples, line.value)) is not None
    ]
    if not lines_with_points:
        return ""

    all_values = [value for _line, points in lines_with_points for _x, value in points]
    max_second = max((s.at_second for s in samples), default=0.0) or 1.0
    min_y, max_y = min(all_values), max(all_values)
    if min_y == max_y:
        # Serie plate (ex. 0 erreur du debut a la fin) : plage artificielle
        # pour eviter une division par zero, le trait reste horizontal.
        min_y, max_y = min_y - 1, max_y + 1

    plot_width = _CHART_WIDTH - _MARGIN_LEFT - _MARGIN_RIGHT
    plot_height = _CHART_HEIGHT - _MARGIN_TOP - _MARGIN_BOTTOM

    def to_svg_x(at_second: float) -> float:
        return _MARGIN_LEFT + (at_second / max_second) * plot_width

    def to_svg_y(value: float) -> float:
        return _MARGIN_TOP + (1 - (value - min_y) / (max_y - min_y)) * plot_height

    parts: list[str] = [
        (
            f'<svg viewBox="0 0 {_CHART_WIDTH} {_CHART_HEIGHT}" width="{_CHART_WIDTH}" '
            f'height="{_CHART_HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{escape(title)}">'
        ),
        (
            f'<text x="{_MARGIN_LEFT}" y="16" font-size="13" font-weight="bold" '
            f'font-family="ui-monospace, monospace" fill="{palette.foreground}">'
            f"{escape(title)}</text>"
        ),
    ]
    parts.append(
        _axes_svg(palette, plot_width=plot_width, plot_height=plot_height, min_y=min_y, max_y=max_y)
    )

    legend_x = _MARGIN_LEFT
    for line, points in lines_with_points:
        path_points = " ".join(f"{to_svg_x(x):.1f},{to_svg_y(y):.1f}" for x, y in points)
        parts.append(
            f'<polyline points="{path_points}" fill="none" stroke="{line.color}" '
            f'stroke-width="2" stroke-linejoin="round"/>'
        )
        parts.append(
            f'<circle cx="{legend_x + 5}" cy="{_CHART_HEIGHT - 6}" r="4" fill="{line.color}"/>'
        )
        parts.append(
            f'<text x="{legend_x + 14}" y="{_CHART_HEIGHT - 2}" font-size="10" '
            f'font-family="ui-monospace, monospace" fill="{palette.foreground}">'
            f"{escape(line.label)}</text>"
        )
        legend_x += 14 + len(line.label) * 6 + 16

    parts.append("</svg>")
    return "".join(parts)


def _points(
    samples: Sequence[IntervalSample], value: Callable[[IntervalSample], float | None]
) -> list[tuple[float, float]] | None:
    """Extrait les points (at_second, valeur) exploitables d'une serie —
    None si AUCUN echantillon n'a de valeur (serie a omettre entierement,
    voir render_time_series_chart). Sous-echantillonne au-dela de
    _MAX_CHART_POINTS (voir _downsample())."""
    points = [(s.at_second, v) for s in samples if (v := value(s)) is not None]
    if not points:
        return None
    return _downsample(points)


def _downsample(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Regroupe les points en paquets consecutifs de taille egale et les
    remplace par leur moyenne (x, y) — evite un SVG demesure sur un run
    long (profil D6 soak, jusqu'a 7200 echantillons) sans changer la
    forme generale de la courbe. Ne s'applique jamais en dessous de
    _MAX_CHART_POINTS : un run court garde chaque point exact."""
    if len(points) <= _MAX_CHART_POINTS:
        return points
    bucket_size = ceil(len(points) / _MAX_CHART_POINTS)
    buckets = [points[i : i + bucket_size] for i in range(0, len(points), bucket_size)]
    return [
        (sum(x for x, _y in bucket) / len(bucket), sum(y for _x, y in bucket) / len(bucket))
        for bucket in buckets
    ]


def _axes_svg(
    palette: Palette, *, plot_width: float, plot_height: float, min_y: float, max_y: float
) -> str:
    parts: list[str] = [
        f'<line x1="{_MARGIN_LEFT}" y1="{_MARGIN_TOP}" x2="{_MARGIN_LEFT}" '
        f'y2="{_MARGIN_TOP + plot_height}" stroke="{palette.secondary}" stroke-width="1"/>',
        f'<line x1="{_MARGIN_LEFT}" y1="{_MARGIN_TOP + plot_height}" '
        f'x2="{_MARGIN_LEFT + plot_width}" y2="{_MARGIN_TOP + plot_height}" '
        f'stroke="{palette.secondary}" stroke-width="1"/>',
    ]
    for tick in range(_Y_TICKS + 1):
        fraction = tick / _Y_TICKS
        y_value = max_y - fraction * (max_y - min_y)
        y_pos = _MARGIN_TOP + fraction * plot_height
        parts.append(
            f'<text x="{_MARGIN_LEFT - 6}" y="{y_pos + 3:.1f}" font-size="9" text-anchor="end" '
            f'font-family="ui-monospace, monospace" fill="{palette.secondary}">{y_value:.0f}</text>'
        )
    return "".join(parts)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - render_time_series_chart() : trace N series sur un axe temporel
#   commun (IntervalSample.at_second), une polyline par serie.
# Pourquoi dans infrastructure/exporters/ (charte) :
# - Meme raisonnement que family_chart.py : detail de rendu visuel d'un
#   export, jamais du calcul metier (les valeurs tracees sont deja
#   presentes sur IntervalSample, calculees ailleurs).
# Ce qu'il ne contient PAS :
# - Aucun import Jinja2 (voir html_exporter.py, seul point du projet ou
#   il est importe).
# - Aucune connaissance de QUELLES series tracer pour quel graphique
#   (RPS/latence/erreurs/CPU-RAM) : c'est html_exporter.py qui construit
#   les TimeSeriesLine et appelle cette fonction 4 fois avec des
#   accesseurs differents — ce fichier reste generique.
# Points cles :
# - Une serie entierement None (ex. aucune mesure systeme disponible sur
#   TOUT le run) est omise silencieusement plutot que tracee a zero, ce
#   qui laisserait croire a une vraie mesure nulle.
# - min_y == max_y (serie plate, ex. 0 erreur partout) : plage +/-1
#   artificielle plutot qu'une division par zero.
# - _downsample() (2026-09-01, runs longs mode "profil" D1-D6, jusqu'a
#   120 min / 7200 echantillons) : moyenne par paquets au-dela de
#   _MAX_CHART_POINTS, appliquee AVANT le calcul de min_y/max_y (donc les
#   deux restent coherents avec les points reellement traces) — jamais
#   applique en dessous du seuil, un run court garde chaque point exact.
#   Aucun autre exporteur (JSON/CSV) n'est concerne, ils gardent
#   l'historique complet des samples.
# - width/height fixes (pas "100%") : meme raison que family_chart.py, un
#   graphique de quelques dizaines de points ne doit pas s'etirer pour
#   remplir la largeur de la page.
# Comment il sera utilise (apercu) :
# - infrastructure/exporters/html_exporter.py appelle cette fonction 4
#   fois (RPS, latence, erreurs, CPU/RAM) avant template.render().
#---------------------------------------------------------------------->
