# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation CSV du port ReportExporter — analyse tabulaire."""
from __future__ import annotations

import csv

from omega_stress.domain.reports.models import ExportJob, ReportContent
from omega_stress.infrastructure.exceptions import StorageError
from omega_stress.infrastructure.exporters.destination_resolver import resolve_destination_file

FIELDNAMES: tuple[str, ...] = (
    "run_id",
    "target_address",
    "family",
    "level",
    "started_at",
    "finished_at",
    "duration_minutes",
    "duration_preset_id",
    "safety_mode",
    "verdict",
    "requested_rate_per_minute",
    "observed_rate_per_minute",
    "p50_latency_ms",
    "p95_latency_ms",
    "p99_latency_ms",
    "error_count",
    "total_requests",
    "errors_timeout",
    "errors_connection",
    "errors_http_4xx",
    "errors_http_5xx",
    "errors_other",
    "peak_cpu_percent_generator",
    "peak_memory_rss_mb",
    "diagnostic_headline",
    "diagnostic_recommendations",
)


class CsvReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter pour le
    format CSV (voir plan produit : "CSV pour analyse tabulaire")."""

    def export(self, content: ReportContent, job: ExportJob) -> str:
        path = resolve_destination_file(job, content.summary, extension="csv")
        row = _content_to_row(content)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerow(row)
        except OSError as exc:
            raise StorageError(f"Echec d'ecriture CSV vers {path} : {exc}") from exc
        return str(path)


def _content_to_row(content: ReportContent) -> dict[str, object]:
    summary, result, diagnostic = content.summary, content.result, content.diagnostic
    return {
        "run_id": summary.run_id,
        "target_address": summary.target_address,
        "family": summary.family.value,
        "level": summary.level.value,
        "started_at": summary.started_at.isoformat(),
        "finished_at": summary.finished_at.isoformat() if summary.finished_at else "",
        "duration_minutes": summary.duration_minutes,
        "duration_preset_id": (
            summary.duration_preset_id.value if summary.duration_preset_id is not None else ""
        ),
        "safety_mode": summary.safety_mode,
        "verdict": result.verdict.value,
        "requested_rate_per_minute": result.requested_rate_per_minute,
        "observed_rate_per_minute": result.observed_rate_per_minute,
        "p50_latency_ms": result.p50_latency_ms,
        "p95_latency_ms": result.p95_latency_ms,
        "p99_latency_ms": result.p99_latency_ms,
        "error_count": result.error_count,
        "total_requests": result.total_requests,
        "errors_timeout": result.errors.timeout,
        "errors_connection": result.errors.connection,
        "errors_http_4xx": result.errors.http_4xx,
        "errors_http_5xx": result.errors.http_5xx,
        "errors_other": result.errors.other,
        "peak_cpu_percent_generator": result.peak_cpu_percent_generator,
        "peak_memory_rss_mb": result.peak_memory_rss_mb,
        "diagnostic_headline": diagnostic.headline,
        "diagnostic_recommendations": "; ".join(diagnostic.recommendations),
    }

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Ecrit une ligne d'en-tete puis UNE ligne de donnees par export
#   (resume + resultat agrege + headline diagnostic).
# Pourquoi dans infrastructure/exporters/ (charte) :
# - Adaptateur remplacable du port report_exporter.py, traduit OSError en
#   StorageError.
# Ce qu'il ne contient PAS :
# - Aucune ligne par intervalle/palier : reste UNE ligne par run (voir
#   test_export_writes_header_and_one_data_row) meme depuis que
#   LoadResult.samples existe (2026-08-24, domain/runs/models.py) — une
#   ligne CSV par seconde denaturerait ce format ("analyse tabulaire d'UN
#   run", pas une serie temporelle) ; l'historique complet reste reserve
#   a json_exporter.py (donnees brutes) et a la chronologie visuelle de
#   html_exporter.py.
# Points cles :
# - FIELDNAMES est exportee (pas prefixee `_`) : reutilisable par un test
#   ou un futur consommateur qui doit connaitre les colonnes attendues
#   sans reparser le fichier.
# - diagnostic_recommendations (2026-08-24, colonne ajoutee) : jointe par
#   "; " en une seule cellule plate — revient sur la decision precedente
#   de ce fichier qui les excluait completement ; desormais possible sans
#   casser le contrat "une ligne par run" puisque c'est une liste de
#   PHRASES (deja formatees par domain/reports/builders.py), pas une serie
#   de mesures qui appellerait une ligne par mesure.
# - path resolu via destination_resolver.py::resolve_destination_file()
#   (2026-08-24), pas Path(job.destination_path) direct : voir son INFO
#   DEV pour le bug corrige (dossier existant traite comme fichier).
# Comment il sera utilise (apercu) :
# - app/dependency_container.py l'enregistre sous ExportFormat.CSV.
#---------------------------------------------------------------------->
