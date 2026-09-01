# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regles metier du sous-domaine reports : pertinence et validite d'un ExportJob."""
from __future__ import annotations

from omega_lib.theme.policies import EXPORT_PALETTES

from omega_stress.core.enums import ExportFormat
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.reports.models import ExportJob


def requires_theme(export_format: ExportFormat) -> bool:
    """Seul le format HTML utilise un theme d'export — JSON/CSV en sont
    independants (voir plan produit, "Sortie" du panneau de tests)."""
    return export_format is ExportFormat.HTML


def validate_export_job(job: ExportJob) -> Result[ExportJob, ValidationError]:
    """Verifie qu'un ExportJob est structurellement valide, notamment que
    le theme d'export reference existe reellement pour un job HTML."""
    if requires_theme(job.format) and job.export_theme not in EXPORT_PALETTES:
        return Err(
            ValidationError(
                f"Theme d'export {job.export_theme!r} inconnu "
                f"(catalogue : {sorted(EXPORT_PALETTES)})."
            )
        )
    return Ok(job)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - requires_theme() : predicat pur sur le format d'export.
# - validate_export_job() : validation structurelle d'un ExportJob avant
#   persistance ou execution de l'export.
# Pourquoi dans domain/reports/ (charte) :
# - Reutilise domain/theme/policies.py::EXPORT_PALETTES comme source de
#   verite unique du catalogue de thèmes d'export, sans le dupliquer
#   (meme logique que domain/profiles/ reutilisant domain/load/policies.py).
# Ce qu'il ne contient PAS :
# - Aucune resolution de palette concrete (c'est
#   infrastructure/exporters/html_theme_resolver.py, un lookup pur execute
#   plus tard, au moment de l'ecriture du fichier).
# - Aucune verification que run_id reference un run existant : c'est le
#   role d'application/commands/export_run_report.py, qui a acces au port
#   run_repository.
# Points cles :
# - Un ExportJob JSON/CSV avec export_theme laisse a sa valeur par defaut
#   ("omega-base") n'est jamais rejete : requires_theme() les exempte de
#   toute verification, la valeur par defaut est simplement ignoree en
#   aval.
# Comment il sera utilise (apercu) :
# - application/commands/export_run_report.py appelle
#   validate_export_job() avant de transmettre le job au port
#   report_exporter.
#---------------------------------------------------------------------->
