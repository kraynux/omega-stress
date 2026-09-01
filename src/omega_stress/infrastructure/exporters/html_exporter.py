# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation HTML du port ReportExporter. Seul fichier du projet ou `jinja2` est importe."""
from __future__ import annotations

from pathlib import Path

import jinja2
from omega_lib.theme.policies import Palette

from omega_stress.domain.reports.models import ExportJob, ReportContent
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.infrastructure.exceptions import StorageError
from omega_stress.infrastructure.exporters.destination_resolver import resolve_destination_file
from omega_stress.infrastructure.exporters.html_theme_resolver import resolve_export_palette
from omega_stress.infrastructure.exporters.time_series_chart import (
    TimeSeriesLine,
    render_time_series_chart,
)

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_TEMPLATE_NAME = "report.html.jinja"


class HtmlReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter pour le
    format HTML (voir plan produit : "HTML pour rapport lisible")."""

    def __init__(self) -> None:
        self._environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(_TEMPLATE_DIR),
            autoescape=jinja2.select_autoescape(["html", "jinja"]),
        )

    def export(self, content: ReportContent, job: ExportJob) -> str:
        palette = resolve_export_palette(job.export_theme)
        template = self._environment.get_template(_TEMPLATE_NAME)
        html = template.render(
            summary=content.summary,
            result=content.result,
            diagnostic=content.diagnostic,
            palette=palette,
            **_render_charts(content.result.samples, palette),
        )

        path = resolve_destination_file(job, content.summary, extension="html")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Echec d'ecriture HTML vers {path} : {exc}") from exc
        return str(path)


def _render_charts(samples: tuple[IntervalSample, ...], palette: Palette) -> dict[str, str]:
    """Construit les 5 graphiques temporels (Phase 1 observabilite) —
    CPU et memoire separes en deux graphiques distincts plutot qu'un
    seul "CPU/RAM" : des pourcentages et des Mo sur un meme axe Y
    fausseraient l'echelle des deux series, pas juste un choix
    cosmetique. Chaque render_time_series_chart() retourne "" si aucun
    echantillon n'a de valeur exploitable pour AUCUNE de ses series —
    le gabarit Jinja2 masque alors ce graphique (meme convention que la
    section Chronologie existante, deja conditionnee sur result.samples)."""
    return {
        "rps_chart": render_time_series_chart(
            samples,
            title="Debit (requetes/min)",
            palette=palette,
            series=(
                TimeSeriesLine("Demande", palette.secondary, lambda s: s.requested_rate_per_minute),
                TimeSeriesLine("Reel", palette.accent, lambda s: s.observed_rate_per_minute),
            ),
        ),
        "latency_chart": render_time_series_chart(
            samples,
            title="Latence (ms)",
            palette=palette,
            series=(
                TimeSeriesLine("p50", palette.success, lambda s: s.p50_latency_ms),
                TimeSeriesLine("p95", palette.warning, lambda s: s.p95_latency_ms),
                TimeSeriesLine("p99", palette.error, lambda s: s.p99_latency_ms),
            ),
        ),
        "errors_chart": render_time_series_chart(
            samples,
            title="Erreurs par categorie",
            palette=palette,
            series=(
                TimeSeriesLine("Timeout", palette.warning, lambda s: float(s.errors.timeout)),
                TimeSeriesLine("Connexion", palette.error, lambda s: float(s.errors.connection)),
                TimeSeriesLine("HTTP 4xx", palette.secondary, lambda s: float(s.errors.http_4xx)),
                TimeSeriesLine("HTTP 5xx", palette.accent, lambda s: float(s.errors.http_5xx)),
            ),
        ),
        "cpu_chart": render_time_series_chart(
            samples,
            title="CPU (%)",
            palette=palette,
            series=(
                TimeSeriesLine(
                    "Generateur",
                    palette.accent,
                    lambda s: s.system.cpu_percent_generator if s.system else None,
                ),
                TimeSeriesLine(
                    "Systeme",
                    palette.secondary,
                    lambda s: s.system.cpu_percent_global if s.system else None,
                ),
            ),
        ),
        "memory_chart": render_time_series_chart(
            samples,
            title="Memoire (Mo)",
            palette=palette,
            series=(
                TimeSeriesLine(
                    "RSS generateur",
                    palette.accent,
                    lambda s: s.system.memory_rss_mb if s.system else None,
                ),
                TimeSeriesLine(
                    "Swap utilise",
                    palette.warning,
                    lambda s: s.system.swap_used_mb if s.system else None,
                ),
            ),
        ),
    }

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Orchestre resolve_export_palette() et le rendu du gabarit Jinja2
#   unique (templates/report.html.jinja), partage par les 5 themes
#   d'export (ARCHITECTURE.md §8 : "un seul gabarit, la palette injectee
#   comme variables de contexte").
# Pourquoi dans infrastructure/exporters/ (charte) :
# - Seul point du projet ou `jinja2` est importe (verifie par le contrat
#   import-linter "jinja2 seulement dans
#   infrastructure.exporters.html_exporter", voir pyproject.toml).
# Ce qu'il ne contient PAS :
# - Aucun lookup de palette (deja fait par html_theme_resolver.py, aucun
#   import Jinja2 a cet endroit).
# - Aucune regle de contenu (headline/recommandations deja construites
#   par domain/reports/builders.py).
# Points cles :
# - path resolu via destination_resolver.py::resolve_destination_file()
#   (2026-08-24), pas Path(job.destination_path) direct : corrige un
#   crash reel — voir son INFO DEV et interfaces/tui/app.py::
#   _handle_exception() pour le detail complet de l'incident (dossier
#   existant traite comme fichier + aucun filet de securite TUI, cumules).
# - autoescape actif (jinja2.select_autoescape) : les champs texte libres
#   (target_address, notes) sont echappes automatiquement, evite toute
#   injection HTML depuis une donnee utilisateur (adresse de cible
#   saisie librement).
# - Section "Chronologie" (2026-08-24, dans le gabarit) : un tableau par
#   IntervalSample (result.samples, voir domain/runs/models.py) avec une
#   barre CSS proportionnelle au taux d'erreur par intervalle, en pur
#   CSS (pas de JS, pas de dependance externe — coherent avec "pas de
#   moteur externe" deja pose pour le runner lui-meme). Masquee via
#   {% if result.samples %} pour un run interrompu avant le premier
#   intervalle (samples vide, deja un cas gere par aggregate_samples()).
#   Aucun code Python ici ne change : result.samples est deja porte par
#   ReportContent.result (le LoadResult transmis tel quel), ce fichier ne
#   fait qu'exposer une donnee deja presente dans le contexte du gabarit.
# - _render_charts() (Phase 1 observabilite) : 5 graphiques SVG calcules
#   ICI, jamais dans le gabarit (Jinja2 ne fait pas de calcul de mise en
#   page) — voir time_series_chart.py pour la technique de rendu. Chaque
#   graphique absent (chaine vide) est masque cote gabarit, meme
#   convention que la section Chronologie ci-dessus.
# - L'environnement Jinja2 est cree une fois par instance (dans
#   __init__), pas a chaque export() : evite de recharger le gabarit a
#   chaque appel.
# - _TEMPLATE_DIR doit rester embarque au packaging (voir pyproject.toml
#   [tool.hatch.build.targets.wheel.force-include], deja configure) —
#   piege connu du plan produit sinon l'export HTML echoue au runtime
#   apres installation alors que les tests locaux passent.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py l'enregistre sous ExportFormat.HTML.
#---------------------------------------------------------------------->
