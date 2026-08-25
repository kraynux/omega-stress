# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : orchestre le listage, le detail et l'export d'un run."""
from __future__ import annotations

from omega_stress.application.commands.clear_run_history import (
    clear_run_history as _clear_run_history,
)
from omega_stress.application.commands.export_run_report import export_run_report
from omega_stress.application.dto.export_dto import ExportRequestDTO, ExportResultDTO
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.queries.get_run_details import get_run_details
from omega_stress.application.queries.list_history import list_history
from omega_stress.core.enums import ExportFormat
from omega_stress.core.results import Result
from omega_stress.domain.errors import ValidationError
from omega_stress.interfaces.tui.presenters.history_presenter import most_recent_first
from omega_stress.ports.export_repository import ExportRepository
from omega_stress.ports.report_exporter import ReportExporter
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.clock import utc_now
from omega_stress.shared.ids import new_id


def load_history(
    *,
    run_repository: RunRepository,
    target_repository: TargetRepository,
    target_id: str | None = None,
    profile_id: str | None = None,
    limit: int = 50,
) -> tuple[RunDTO, ...]:
    """Historique pret pour l'affichage (plus recents d'abord, voir
    presenters/history_presenter.py)."""
    runs = list_history(
        run_repository=run_repository,
        target_repository=target_repository,
        target_id=target_id,
        profile_id=profile_id,
        limit=limit,
    )
    return most_recent_first(runs)


def run_details(
    run_id: str, *, run_repository: RunRepository, target_repository: TargetRepository
) -> RunDTO | None:
    """Detail d'un run pour screens/run_details.py."""
    return get_run_details(
        run_id, run_repository=run_repository, target_repository=target_repository
    )


def clear_run_history(*, run_repository: RunRepository) -> None:
    """Vide tout l'historique des runs (screens/settings_screen.py,
    "Vider l'historique")."""
    _clear_run_history(run_repository=run_repository)


async def export_report(
    run_id: str,
    *,
    export_format: ExportFormat,
    destination_path: str,
    export_theme: str,
    run_repository: RunRepository,
    target_repository: TargetRepository,
    export_repository: ExportRepository,
    exporters: dict[ExportFormat, ReportExporter],
) -> Result[ExportResultDTO, ValidationError]:
    """Exporte le rapport d'un run termine, depuis screens/export_dialog.py."""
    request = ExportRequestDTO(
        run_id=run_id,
        format=export_format.value,
        destination_path=destination_path,
        export_theme=export_theme,
    )
    return await export_run_report(
        request,
        run_repository=run_repository,
        target_repository=target_repository,
        export_repository=export_repository,
        exporters=exporters,
        id_factory=new_id,
        now=utc_now(),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de screens/history.py, screens/run_details.py et
#   screens/export_dialog.py vers application/queries/ et
#   application/commands/export_run_report.py pour tout ce qui concerne
#   l'historique et l'export d'un run.
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - Applique systematiquement le tri d'affichage (presenters/
#   history_presenter.py) : aucun ecran ne doit appeler
#   application/queries/list_history.py directement.
# - Aucun controller dedie a l'export dans ARCHITECTURE.md §2 (6
#   controllers exactement) : l'export ne concerne QUE des runs deja
#   historises, il rejoint donc naturellement ce controller plutot que
#   d'en creer un septieme.
# Ce qu'il ne contient PAS :
# - Aucun declenchement de relecture ("rejouer") : voir
#   load_controller.py::launch_replay(), sous-domaine execution, pas
#   lecture d'historique.
# Points cles :
# - run_details() peut retourner None (run introuvable) : transmis tel
#   quel, a l'ecran de decider de l'affichage ("run introuvable").
# - target_repository (2026-08-25) desormais requis par load_history() et
#   run_details() (pas seulement export_report()) : les deux resolvent
#   maintenant RunDTO.target_address (adresse humaine), voir
#   application/queries/get_run_details.py et list_history.py pour le
#   detail du bug corrige.
# - export_report() construit lui-meme l'ExportRequestDTO : l'ecran ne
#   manipule que des primitives (run_id, format, chemin, theme), jamais ce
#   DTO directement.
# - clear_run_history() (2026-08-24) : simple relais vers le command
#   homonyme, aucune confirmation ici — deja geree cote ecran
#   (screens/confirm.py) avant l'appel. Rejoint ce controller plutot que
#   load_controller.py : c'est une purge d'HISTORIQUE (runs), pas une
#   operation de cible.
# Comment il sera utilise :
# - screens/history.py, screens/run_details.py, screens/export_dialog.py,
#   screens/settings_screen.py (purge de l'historique).
#---------------------------------------------------------------------->
