# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : exporter le rapport d'un run termine."""
from __future__ import annotations

from datetime import datetime

from omega_stress.application.dto.export_dto import ExportRequestDTO, ExportResultDTO
from omega_stress.core.enums import ExportFormat
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.reports.builders import build_report_content
from omega_stress.domain.reports.models import ExportJob
from omega_stress.domain.reports.service import validate_export_job
from omega_stress.ports.export_repository import ExportRepository
from omega_stress.ports.report_exporter import ReportExporter
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import IdFactory


async def export_run_report(
    request: ExportRequestDTO,
    *,
    run_repository: RunRepository,
    target_repository: TargetRepository,
    export_repository: ExportRepository,
    exporters: dict[ExportFormat, ReportExporter],
    id_factory: IdFactory,
    now: datetime,
) -> Result[ExportResultDTO, ValidationError]:
    """Construit le contenu logique du rapport (domain/reports/builders.py)
    et l'ecrit via l'exporter concret correspondant au format demande."""
    run = run_repository.get(request.run_id)
    if run is None:
        return Err(ValidationError(f"Run {request.run_id!r} introuvable."))
    if run.finished_at is None:
        return Err(ValidationError(f"Run {request.run_id!r} n'est pas encore termine."))

    try:
        export_format = ExportFormat(request.format)
    except ValueError:
        return Err(ValidationError(f"Format d'export {request.format!r} inconnu."))

    job = ExportJob(
        id=id_factory(),
        run_id=request.run_id,
        format=export_format,
        destination_path=request.destination_path,
        created_at=now,
        export_theme=request.export_theme,
    )
    validated_job = validate_export_job(job)
    if isinstance(validated_job, Err):
        return validated_job

    target = target_repository.get(run.target_id)
    target_address = target.address.base_url if target is not None else run.target_id

    content = build_report_content(run, target_address=target_address)

    exporter = exporters[export_format]
    written_path = exporter.export(content, validated_job.value)
    export_repository.save(validated_job.value)

    return Ok(ExportResultDTO(job_id=validated_job.value.id, written_path=written_path))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Enchaine verification (run termine, format connu, theme valide pour
#   HTML), construction du contenu logique, ecriture concrete et
#   tracabilite (export_repository).
# Pourquoi dans application/commands/ (charte) :
# - Orchestre domain/reports/builders.py, domain/reports/service.py et
#   deux ports (report_exporter, export_repository), sans regle metier
#   propre.
# Ce qu'il ne contient PAS :
# - Aucune serialisation JSON/CSV/HTML : deleguee entierement a
#   l'exporter concret choisi dans `exporters`.
# - Aucune resolution de theme d'export vers une palette concrete (c'est
#   infrastructure/exporters/html_theme_resolver.py, appele par
#   l'implementation HTML de ReportExporter, jamais ici).
# Points cles :
# - `exporters: dict[ExportFormat, ReportExporter]` plutot qu'un exporter
#   unique : il existe un adaptateur par format
#   (infrastructure/exporters/{json,csv,html}_exporter.py, voir
#   ports/report_exporter.py) et ce command choisit celui qui correspond
#   au format demande — la selection reste du ressort d'application/, pas
#   d'un mecanisme cache dans infrastructure/.
# - target_address se replie sur run.target_id si la cible a ete
#   supprimee entre-temps : un rapport reste exportable meme si la cible
#   n'existe plus dans le repository, avec un identifiant brut plutot
#   qu'une adresse lisible.
# - build_report_content() peut lever ValueError si run.result est None
#   malgre finished_at non-None (etat incoherent normalement impossible,
#   voir domain/runs/service.py::finish()) : laisse deliberement remonter,
#   ce serait un bug d'invariant, pas un echec metier attendu.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/export_dialog.py,
#   interfaces/cli/commands/export_command.py.
#---------------------------------------------------------------------->
