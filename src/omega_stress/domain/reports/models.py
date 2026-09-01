# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites du sous-domaine reports : job d'export et contenu logique d'un rapport."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_stress.core.enums import (
    DurationPresetId,
    ExportFormat,
    IntensityLevel,
    RunVerdict,
    TestFamily,
)
from omega_stress.domain.runs.models import LoadResult


@dataclass(frozen=True, slots=True)
class ExportJob:
    """Demande d'export d'un run, dans un format et vers une destination
    donnes (voir plan produit, "Export detaille")."""

    id: str
    run_id: str
    format: ExportFormat
    destination_path: str
    created_at: datetime
    export_theme: str = "omega-base"


@dataclass(frozen=True, slots=True)
class ReportSummary:
    """Box resume d'un rapport : cible, date, duree, type (voir plan
    produit, "Diagnostic et affichage du rapport")."""

    run_id: str
    target_address: str
    family: TestFamily
    level: IntensityLevel
    started_at: datetime
    finished_at: datetime | None
    duration_minutes: float
    duration_preset_id: DurationPresetId | None = None
    safety_mode: bool = True


@dataclass(frozen=True, slots=True)
class ReportDiagnostic:
    """Box diagnostic : interpretation et recommandations, construites a
    partir du verdict et des metriques, jamais d'un message d'exception
    libre."""

    verdict: RunVerdict
    headline: str
    recommendations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportContent:
    """Contenu logique complet d'un rapport, independant de tout format de
    sortie concret (JSON/CSV/HTML)."""

    summary: ReportSummary
    result: LoadResult
    diagnostic: ReportDiagnostic

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - ExportJob : demande d'export persistee (format, destination, theme
#   pour le cas HTML).
# - ReportSummary / ReportDiagnostic / ReportContent : contenu LOGIQUE d'un
#   rapport (les "box" du plan produit), assemble par
#   domain/reports/builders.py, avant toute serialisation concrete.
# Pourquoi dans domain/reports/ (charte) :
# - Entites/VO metier pures. ReportContent est deliberement independant du
#   format final : infrastructure/exporters/{json,csv,html}_exporter.py le
#   consomment tous les trois sans qu'aucun ne redefinisse sa propre
#   notion de "contenu de rapport".
# Ce qu'il ne contient PAS :
# - Aucun template Jinja2, aucune chaine JSON/CSV serialisee : voir
#   ARCHITECTURE.md §0 (tableau des ecarts) — deliberement different de
#   l'exemple omega-fire qui listait des templates dans domain/reports/.
# - Aucune table de paliers de rampe individuelle : deja portee par
#   LoadResult.events (RunEvent) si pertinent, pas dupliquee ici.
# Points cles :
# - ExportJob.export_theme n'a de sens que pour ExportFormat.HTML (voir
#   domain/reports/service.py::requires_theme) ; sa presence pour
#   JSON/CSV est inoffensive mais ignoree par les exporters concernes.
# - ReportContent.result reutilise LoadResult tel quel (domain/runs/) :
#   pas de duplication de champ metrique entre les deux sous-domaines.
# - ReportSummary.duration_preset_id (2026-09-01, mode "profil" D1-D6) :
#   copie de LoadRun.duration_preset_id, None pour un run en mode manuel.
# - ReportSummary.safety_mode (2026-09-01, "mode securite" a cocher) :
#   copie de LoadRun.safety_mode, pour qu'un rapport dise honnetement si
#   les garde-fous locaux (CPU/memoire/FDs) etaient actifs pendant ce run.
# Comment il sera utilise (apercu) :
# - domain/reports/builders.py::build_report_content() produit un
#   ReportContent a partir d'un LoadRun termine.
# - application/commands/export_run_report.py orchestre ExportJob ->
#   ReportContent -> port report_exporter.
#---------------------------------------------------------------------->
