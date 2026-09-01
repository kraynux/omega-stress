# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation JSON du port ReportExporter — donnees brutes et reimport."""
from __future__ import annotations

import json
from typing import Any

from omega_stress.domain.reports.models import ExportJob, ReportContent
from omega_stress.infrastructure.exceptions import StorageError
from omega_stress.infrastructure.exporters.destination_resolver import resolve_destination_file


class JsonReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter pour le
    format JSON (voir plan produit : "JSON pour donnees brutes et
    reimport")."""

    def export(self, content: ReportContent, job: ExportJob) -> str:
        payload = _content_to_dict(content)
        path = resolve_destination_file(job, content.summary, extension="json")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
        except OSError as exc:
            raise StorageError(f"Echec d'ecriture JSON vers {path} : {exc}") from exc
        return str(path)


def _content_to_dict(content: ReportContent) -> dict[str, Any]:
    summary, result, diagnostic = content.summary, content.result, content.diagnostic
    return {
        "summary": {
            "run_id": summary.run_id,
            "target_address": summary.target_address,
            "family": summary.family.value,
            "level": summary.level.value,
            "started_at": summary.started_at.isoformat(),
            "finished_at": summary.finished_at.isoformat() if summary.finished_at else None,
            "duration_minutes": summary.duration_minutes,
            "duration_preset_id": (
                summary.duration_preset_id.value if summary.duration_preset_id is not None else None
            ),
            "safety_mode": summary.safety_mode,
        },
        "result": {
            "verdict": result.verdict.value,
            "requested_rate_per_minute": result.requested_rate_per_minute,
            "observed_rate_per_minute": result.observed_rate_per_minute,
            "p50_latency_ms": result.p50_latency_ms,
            "p95_latency_ms": result.p95_latency_ms,
            "p99_latency_ms": result.p99_latency_ms,
            "error_count": result.error_count,
            "total_requests": result.total_requests,
            "errors": {
                "timeout": result.errors.timeout,
                "connection": result.errors.connection,
                "http_4xx": result.errors.http_4xx,
                "http_5xx": result.errors.http_5xx,
                "other": result.errors.other,
            },
            "peak_cpu_percent_generator": result.peak_cpu_percent_generator,
            "peak_memory_rss_mb": result.peak_memory_rss_mb,
            "events": [
                {
                    "occurred_at": e.occurred_at.isoformat(),
                    "kind": e.kind,
                    "message": e.message,
                }
                for e in result.events
            ],
            "samples": [
                {
                    "at_second": s.at_second,
                    "observed_rate_per_minute": s.observed_rate_per_minute,
                    "p50_latency_ms": s.p50_latency_ms,
                    "p95_latency_ms": s.p95_latency_ms,
                    "p99_latency_ms": s.p99_latency_ms,
                    "error_count": s.error_count,
                    "request_count": s.request_count,
                    "requested_rate_per_minute": s.requested_rate_per_minute,
                    "active_connections": s.active_connections,
                    "errors": {
                        "timeout": s.errors.timeout,
                        "connection": s.errors.connection,
                        "http_4xx": s.errors.http_4xx,
                        "http_5xx": s.errors.http_5xx,
                        "other": s.errors.other,
                    },
                    "system": (
                        {
                            "cpu_percent_generator": s.system.cpu_percent_generator,
                            "cpu_percent_global": s.system.cpu_percent_global,
                            "memory_available_percent": s.system.memory_available_percent,
                            "memory_rss_mb": s.system.memory_rss_mb,
                            "swap_used_mb": s.system.swap_used_mb,
                            "open_files": s.system.open_files,
                            "open_files_soft_limit": s.system.open_files_soft_limit,
                            "logical_cpu_count": s.system.logical_cpu_count,
                        }
                        if s.system is not None
                        else None
                    ),
                }
                for s in result.samples
            ],
        },
        "diagnostic": {
            "verdict": diagnostic.verdict.value,
            "headline": diagnostic.headline,
            "recommendations": list(diagnostic.recommendations),
        },
    }

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Serialise un ReportContent en JSON indente, sans reference cyclique
#   ni objet non serialisable (enums -> .value, datetimes -> ISO 8601).
# Pourquoi dans infrastructure/exporters/ (charte) :
# - Adaptateur remplacable du port report_exporter.py, traduit
#   OSError en StorageError.
# Ce qu'il ne contient PAS :
# - Aucun theme (le format JSON, contrairement au HTML, n'utilise pas
#   ExportJob.export_theme — un rapport de donnees brutes n'a pas de
#   rendu visuel).
# Points cles :
# - _content_to_dict() est une fonction module-level privee, structure
#   le JSON en trois sections (summary/result/diagnostic), miroir direct
#   de domain/reports/models.py::ReportContent.
# - result.samples (2026-08-24) : tableau complet, un objet par
#   IntervalSample (jusqu'a quelques centaines pour un run au maximum
#   autorise) — c'est le format "donnees brutes et reimport" (docstring
#   du module), l'endroit naturel pour l'historique complet ; CSV garde
#   volontairement une seule ligne par run (voir csv_exporter.py) et HTML
#   en fait un tableau visuel (voir html_exporter.py) plutot que de
#   dupliquer ce meme tableau brut trois fois.
# - path resolu via destination_resolver.py::resolve_destination_file()
#   (2026-08-24), pas Path(job.destination_path) direct : voir son INFO
#   DEV pour le bug corrige (dossier existant traite comme fichier).
# Comment il sera utilise (apercu) :
# - app/dependency_container.py l'enregistre sous ExportFormat.JSON dans
#   le dict `exporters` passe a
#   application/commands/export_run_report.py.
#---------------------------------------------------------------------->
