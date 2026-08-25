# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat d'ecriture concrete d'un rapport (JSON/CSV/HTML)."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.reports.models import ExportJob, ReportContent


class ReportExporter(Protocol):
    """Port consomme par application/, implemente par
    infrastructure/exporters/{json,csv,html}_exporter.py (un adaptateur
    par format, tous conformes a ce meme contrat)."""

    def export(self, content: ReportContent, job: ExportJob) -> str:
        """Ecrit le rapport au format concret decrit par job.format, vers
        job.destination_path. Retourne le chemin effectivement ecrit."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat unique d'ecriture d'un rapport, implemente une fois par
#   format d'export.
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif ("ecrire ce contenu logique dans ce
#   format, a cet endroit"), jamais par l'API Jinja2 ou par la structure
#   d'un fichier CSV — ce port ne fuit aucun detail de format.
# Ce qu'il ne contient PAS :
# - Aucune implementation (voir infrastructure/exporters/).
# - Aucune logique de choix de l'exporter a utiliser selon job.format :
#   c'est application/commands/export_run_report.py (ou
#   app/dependency_container.py) qui selectionne le bon adaptateur
#   concret, jamais ce Protocol lui-meme.
# Points cles :
# - Une seule methode export() : le contrat reste volontairement minimal,
#   chaque format gere ses propres details en interne (template Jinja2
#   pour HTML, structure de colonnes pour CSV, etc.), sans que cela
#   remonte dans la signature.
# Comment il sera utilise (apercu) :
# - application/commands/export_run_report.py appelle export() apres
#   domain/reports/builders.py::build_report_content().
#---------------------------------------------------------------------->
