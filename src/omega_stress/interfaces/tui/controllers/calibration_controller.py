# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : declenche/consulte le calibrage local depuis
screens/calibration_screen.py."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_stress.application.commands.run_calibration import run_calibration
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.core.results import Result
from omega_stress.domain.calibration.exceptions import CalibrationPreconditionError
from omega_stress.domain.calibration.models import CalibrationResult
from omega_stress.domain.calibration.service import compute_fingerprint_hash
from omega_stress.ports.calibration_stage_progress_notifier import (
    CalibrationStageProgressNotifier,
)
from omega_stress.shared.clock import utc_now

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/commands/
    # run_command.py pour la justification complete : exclu du graphe
    # import-linter par exclude_type_checking_imports, jamais execute).
    from omega_stress.app.dependency_container import DependencyContainer


def current_fingerprint_hash(container: DependencyContainer) -> str:
    """Empreinte de la machine courante, cle de consultation du dernier
    resultat persiste (jamais recalculee ailleurs)."""
    return compute_fingerprint_hash(container.compute_calibration_fingerprint())


def load_last_calibration(container: DependencyContainer) -> CalibrationResult | None:
    """Dernier resultat persiste pour la machine courante, ou None si
    jamais calibree."""
    return container.calibration_repository.load(current_fingerprint_hash(container))


async def launch_calibration(
    *,
    container: DependencyContainer,
    notification_sink: NotificationSink,
    stage_progress_notifier: CalibrationStageProgressNotifier,
) -> Result[CalibrationResult, CalibrationPreconditionError]:
    """Lance un calibrage complet depuis screens/calibration_screen.py."""
    return await run_calibration(
        compute_fingerprint=container.compute_calibration_fingerprint,
        preconditions_probe=container.calibration_preconditions_probe,
        server_factory=container.calibration_server_factory,
        stage_runner_factory=container.calibration_stage_runner_factory,
        calibration_repository=container.calibration_repository,
        now=utc_now,
        notification_sink=notification_sink,
        stage_progress_notifier=stage_progress_notifier,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit une action utilisateur de calibrage (consulter le dernier
#   resultat, en lancer un nouveau) en appel a application/commands/
#   run_calibration.py, avec les ports concrets du DependencyContainer.
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - Symetrique a load_controller.py pour son propre sous-domaine — ce
#   controller ne fait qu'assembler des parametres, jamais de logique de
#   guard/evaluation lui-meme (deja dans domain/calibration/validators.py
#   et application/commands/run_calibration.py).
# Ce qu'il ne contient PAS :
# - another_calibration_or_run_active : jamais transmis ici (reste au
#   defaut False de run_calibration()) — aucun mecanisme de detection
#   cross-ecran/cross-processus d'un calibrage/run deja actif n'existe
#   dans ce projet (chaque ecran de lancement ne suit que SON PROPRE
#   worker, voir request_panel.py::self._active_worker) ; construire un
#   tel mecanisme reste un angle mort assume de ce chantier (voir le plan,
#   "Verrou cross-process"), pas un oubli silencieux.
# - Aucune construction de widget : notification_sink est fourni par
#   l'ecran appelant (deja une instance de widgets/notification_bar.py).
# Points cles :
# - CLI (interfaces/cli/commands/calibrate_command.py) NE REUTILISE PAS ce
#   controller : CLI et TUI restent deux adaptateurs independants par
#   choix produit (ARCHITECTURE.md §0, meme raison documentee dans
#   load_controller.py) — le CLI duplique l'appel a run_calibration()
#   directement plutot que d'importer ce module (interfaces/tui/ et
#   interfaces/cli/ ne se referencent jamais l'un l'autre).
# Comment il sera utilise :
# - screens/calibration_screen.py (bouton "Lancer le calibrage",
#   consultation du dernier resultat connu a l'ouverture de l'ecran).
#---------------------------------------------------------------------->
