# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de persistance des jobs d'export."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.reports.models import ExportJob


class ExportRepository(Protocol):
    """Port consomme par application/, implemente par
    infrastructure/storage/sqlite/export_repository.py."""

    def save(self, job: ExportJob) -> None: ...

    def list_for_run(self, run_id: str) -> tuple[ExportJob, ...]: ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de tracabilite des exports realises pour un run donne.
# Pourquoi dans ports/ (charte) :
# - Distinct de report_exporter.py : ce port persiste la METADATA du job
#   (quand, quel format, vers ou), report_exporter.py ECRIT le fichier
#   concret — deux responsabilites, deux ports.
# Ce qu'il ne contient PAS :
# - Aucune ecriture de fichier de rapport (voir ports/report_exporter.py).
# - Aucune validation (voir domain/reports/service.py::validate_export_job,
#   appele par l'application avant de sauvegarder via ce port).
# Points cles :
# - list_for_run() permet de retrouver l'historique des exports d'un run
#   (plan produit : "exporter un run" comme action repetable, traçable).
# Comment il sera utilise (apercu) :
# - application/commands/export_run_report.py sauvegarde l'ExportJob ici
#   apres avoir ecrit le fichier via ports/report_exporter.py.
#---------------------------------------------------------------------->
