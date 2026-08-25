# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation SQLite du port ExportRepository."""
from __future__ import annotations

import sqlite3
from datetime import datetime

from omega_stress.core.enums import ExportFormat
from omega_stress.domain.reports.models import ExportJob
from omega_stress.infrastructure.exceptions import StorageError


class SqliteExportRepository:
    """Implemente ports/export_repository.py::ExportRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, job: ExportJob) -> None:
        try:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO export_jobs (
                    id, run_id, format, destination_path, export_theme, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.run_id,
                    job.format.value,
                    job.destination_path,
                    job.export_theme,
                    job.created_at.isoformat(),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de sauvegarde du job d'export {job.id!r} : {exc}") from exc

    def list_for_run(self, run_id: str) -> tuple[ExportJob, ...]:
        try:
            rows = self._connection.execute(
                "SELECT * FROM export_jobs WHERE run_id = ? ORDER BY created_at DESC", (run_id,)
            ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de listage des exports du run {run_id!r} : {exc}") from exc
        return tuple(_row_to_export_job(row) for row in rows)


def _row_to_export_job(row: sqlite3.Row) -> ExportJob:
    return ExportJob(
        id=row["id"],
        run_id=row["run_id"],
        format=ExportFormat(row["format"]),
        destination_path=row["destination_path"],
        created_at=datetime.fromisoformat(row["created_at"]),
        export_theme=row["export_theme"],
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Implementation concrete du port export_repository.py : tracabilite
#   des exports realises, pas l'ecriture du fichier lui-meme (voir
#   infrastructure/exporters/, qui implemente ports/report_exporter.py
#   separement).
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Adaptateur remplacable, traduit sqlite3.Error en StorageError.
# Ce qu'il ne contient PAS :
# - Aucune ecriture de fichier JSON/CSV/HTML.
# - Aucune validation (deja faite par
#   domain/reports/service.py::validate_export_job() avant que save() ne
#   soit appele).
# Points cles :
# - La plus simple des quatre repositories SQLite : deux methodes
#   seulement (save/list_for_run), pas de get() individuel — coherent
#   avec ports/export_repository.py, qui n'en definit pas.
# Comment il sera utilise (apercu) :
# - application/commands/export_run_report.py.
#---------------------------------------------------------------------->
