# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : declenche precheck/request/connection/ramp/replay depuis
les ecrans de lancement du TUI (request_panel.py, connection_panel.py,
ramp_panel.py, history.py)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_stress.application.commands._launch_support import LaunchError
from omega_stress.application.commands.clear_all_targets import (
    clear_all_targets as _clear_all_targets,
)
from omega_stress.application.commands.clear_recent_targets import (
    clear_recent_targets as _clear_recent_targets,
)
from omega_stress.application.commands.pin_target import pin_target as _pin_target
from omega_stress.application.commands.replay_run import replay_run
from omega_stress.application.commands.run_connection_load import run_connection_load
from omega_stress.application.commands.run_precheck import run_precheck
from omega_stress.application.commands.run_ramp_load import run_ramp_load
from omega_stress.application.commands.run_request_load import run_request_load
from omega_stress.application.commands.unpin_target import unpin_target as _unpin_target
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.application.queries.list_targets import list_targets
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Result
from omega_stress.domain.errors import UnauthorizedTargetError, ValidationError
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.load.validators import PlanValidationError
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.clock import utc_now
from omega_stress.shared.ids import new_id

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/commands/
    # run_command.py pour la justification complete : exclu du graphe
    # import-linter par exclude_type_checking_imports, jamais execute).
    from omega_stress.app.dependency_container import DependencyContainer

LoadLaunchError = UnauthorizedTargetError | LaunchError


def ensure_capabilities_probed(container: DependencyContainer) -> None:
    """Peuple core/capability_registry.py depuis un sondage frais avant
    tout lancement, sans quoi un lancement Haut/Maximum leverait
    CapabilityRegistryError au lieu d'un refus controle. Duplique de
    interfaces/cli/commands/run_command.py::_ensure_capabilities_probed()
    plutot que partage : CLI et TUI restent deux adaptateurs independants
    par choix produit (ARCHITECTURE.md §0), chacun assemble ses propres
    parametres pour application/."""
    for capability in container.system_probe.probe():
        container.capability_registry.register(capability)


async def launch_precheck(
    *,
    container: DependencyContainer,
    target_id: str,
    target_url: str,
    explicit_confirmation: bool,
    run_progress_notifier: RunProgressNotifier,
    notification_sink: NotificationSink,
) -> Result[RunDTO, PlanValidationError | UnauthorizedTargetError]:
    """Lance un Pre-check depuis un ecran de lancement, avant d'autoriser
    un niveau Haut/Maximum."""
    return await run_precheck(
        target_id=target_id,
        target_url=target_url,
        target_repository=container.target_repository,
        load_runner=container.load_runner,
        run_progress_notifier=run_progress_notifier,
        run_repository=container.run_repository,
        audit_sink=container.audit_logger.record,
        notification_sink=notification_sink,
        id_factory=new_id,
        explicit_confirmation=explicit_confirmation,
        now=utc_now,
    )


async def launch_request(
    *,
    container: DependencyContainer,
    target_id: str,
    target_url: str,
    level: IntensityLevel,
    duration_minutes: int,
    thresholds: Thresholds,
    explicit_confirmation: bool,
    precheck_validated: bool,
    run_progress_notifier: RunProgressNotifier,
    notification_sink: NotificationSink,
    profile_id: str | None = None,
) -> Result[RunDTO, LoadLaunchError]:
    """Lance un Test requetes depuis screens/request_panel.py."""
    ensure_capabilities_probed(container)
    return await run_request_load(
        **_load_kwargs(
            container=container,
            target_id=target_id,
            target_url=target_url,
            level=level,
            duration_minutes=duration_minutes,
            thresholds=thresholds,
            explicit_confirmation=explicit_confirmation,
            precheck_validated=precheck_validated,
            run_progress_notifier=run_progress_notifier,
            notification_sink=notification_sink,
            profile_id=profile_id,
        )
    )


async def launch_connection(
    *,
    container: DependencyContainer,
    target_id: str,
    target_url: str,
    level: IntensityLevel,
    duration_minutes: int,
    thresholds: Thresholds,
    explicit_confirmation: bool,
    precheck_validated: bool,
    run_progress_notifier: RunProgressNotifier,
    notification_sink: NotificationSink,
    profile_id: str | None = None,
) -> Result[RunDTO, LoadLaunchError]:
    """Lance un Test connexions depuis screens/connection_panel.py."""
    ensure_capabilities_probed(container)
    return await run_connection_load(
        **_load_kwargs(
            container=container,
            target_id=target_id,
            target_url=target_url,
            level=level,
            duration_minutes=duration_minutes,
            thresholds=thresholds,
            explicit_confirmation=explicit_confirmation,
            precheck_validated=precheck_validated,
            run_progress_notifier=run_progress_notifier,
            notification_sink=notification_sink,
            profile_id=profile_id,
        )
    )


async def launch_ramp(
    *,
    container: DependencyContainer,
    target_id: str,
    target_url: str,
    level: IntensityLevel,
    duration_minutes: int,
    thresholds: Thresholds,
    explicit_confirmation: bool,
    precheck_validated: bool,
    run_progress_notifier: RunProgressNotifier,
    notification_sink: NotificationSink,
    profile_id: str | None = None,
) -> Result[RunDTO, LoadLaunchError]:
    """Lance un Test charge (montee progressive) depuis screens/ramp_panel.py."""
    ensure_capabilities_probed(container)
    return await run_ramp_load(
        **_load_kwargs(
            container=container,
            target_id=target_id,
            target_url=target_url,
            level=level,
            duration_minutes=duration_minutes,
            thresholds=thresholds,
            explicit_confirmation=explicit_confirmation,
            precheck_validated=precheck_validated,
            run_progress_notifier=run_progress_notifier,
            notification_sink=notification_sink,
            profile_id=profile_id,
        )
    )


async def launch_replay(
    run_id: str,
    *,
    container: DependencyContainer,
    explicit_confirmation: bool,
    precheck_validated: bool,
    run_progress_notifier: RunProgressNotifier,
    notification_sink: NotificationSink,
) -> Result[RunDTO, ValidationError | LoadLaunchError]:
    """Rejoue un run existant depuis screens/history.py (action "relancer")."""
    ensure_capabilities_probed(container)
    return await replay_run(
        run_id,
        run_repository=container.run_repository,
        profile_repository=container.profile_repository,
        target_repository=container.target_repository,
        load_runner=container.load_runner,
        run_progress_notifier=run_progress_notifier,
        audit_sink=container.audit_logger.record,
        notification_sink=notification_sink,
        id_factory=new_id,
        explicit_confirmation=explicit_confirmation,
        precheck_validated=precheck_validated,
        now=utc_now,
        capability_registry=container.capability_registry,
    )


def load_targets(*, target_repository: TargetRepository) -> tuple[TargetDTO, ...]:
    """Cibles epinglees puis recentes, pour widgets/target_picker.py."""
    return list_targets(target_repository=target_repository)


def pin_new_target(
    *,
    target_repository: TargetRepository,
    raw_address: str,
    authorization_confirmed: bool,
    tags: tuple[str, ...] = (),
    notes: str = "",
) -> Result[TargetDTO, ValidationError | UnauthorizedTargetError]:
    """Epingle une nouvelle cible saisie manuellement (widgets/
    target_picker.py, action "epingler")."""
    return _pin_target(
        target_repository=target_repository,
        id_factory=new_id,
        now=utc_now(),
        raw_address=raw_address,
        authorization_confirmed=authorization_confirmed,
        tags=tags,
        notes=notes,
    )


def unpin_existing_target(target_id: str, *, target_repository: TargetRepository) -> None:
    """Desepingle une cible (widgets/target_picker.py, action "desepingler")."""
    _unpin_target(target_id, target_repository=target_repository)


def clear_recent_targets(*, target_repository: TargetRepository) -> None:
    """Vide les cibles recentes (screens/settings_screen.py, "Vider les
    cibles recentes")."""
    _clear_recent_targets(target_repository=target_repository)


def clear_all_targets(*, target_repository: TargetRepository) -> None:
    """Efface toutes les cibles, y compris epinglees (screens/
    settings_screen.py, "Effacer toutes les cibles")."""
    _clear_all_targets(target_repository=target_repository)


def _load_kwargs(
    *,
    container: DependencyContainer,
    target_id: str,
    target_url: str,
    level: IntensityLevel,
    duration_minutes: int,
    thresholds: Thresholds,
    explicit_confirmation: bool,
    precheck_validated: bool,
    run_progress_notifier: RunProgressNotifier,
    notification_sink: NotificationSink,
    profile_id: str | None,
) -> dict:
    return dict(
        target_id=target_id,
        target_url=target_url,
        level=level,
        duration_minutes=duration_minutes,
        thresholds=thresholds,
        explicit_confirmation=explicit_confirmation,
        precheck_validated=precheck_validated,
        profile_id=profile_id,
        target_repository=container.target_repository,
        load_runner=container.load_runner,
        run_progress_notifier=run_progress_notifier,
        run_repository=container.run_repository,
        audit_sink=container.audit_logger.record,
        notification_sink=notification_sink,
        id_factory=new_id,
        now=utc_now,
        capability_registry=container.capability_registry,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit une action utilisateur de lancement (precheck/request/
#   connection/ramp/replay), ou de gestion des cibles (list/pin/unpin,
#   necessaires a widgets/target_picker.py), en appel au command
#   application/ correspondant,
#   avec les ports concrets du DependencyContainer et les composants de
#   presentation TUI injectes par l'appelant (run_progress_notifier,
#   notification_sink).
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - Symetrique a interfaces/cli/commands/run_command.py cote CLI, avec la
#   meme sequence guard/execution (deja geree par application/pipeline/
#   et application/commands/_launch_support.py) — ce controller ne fait
#   qu'assembler des parametres, jamais de logique de guard lui-meme.
# Ce qu'il ne contient PAS :
# - Aucune construction de widget (ProgressPanel, NotificationBar...) :
#   run_progress_notifier et notification_sink sont fournis par l'ecran
#   appelant (deja des instances de widgets/progress_panel.py et
#   widgets/notification_bar.py, ce dernier etant lui-meme un
#   NotificationSink via son __call__).
# - Aucun formatage pour affichage : retourne un Result[RunDTO, ...] brut,
#   a mettre en forme par presenters/run_presenter.py cote ecran.
# Points cles :
# - ensure_capabilities_probed() est appelee avant CHAQUE lancement (pas
#   seulement au demarrage) : un sondage frais reste peu couteux
#   (infrastructure/probe/local_probe.py) et garantit que le pre-flight
#   check reste a jour meme si les ressources systeme ont change entre
#   deux runs.
# - launch_precheck() n'appelle PAS ensure_capabilities_probed() : un
#   Pre-check est toujours de niveau Bas (voir run_precheck.py), jamais
#   soumis au guard de capacite.
# - Aucun target_controller.py dedie n'existe dans ARCHITECTURE.md §2 (6
#   controllers exactement) : les operations de cible (list/pin/unpin,
#   clear_recent/clear_all) n'ont de sens que pour alimenter
#   widgets/target_picker.py et screens/settings_screen.py — elles
#   rejoignent donc naturellement ce controller plutot que d'en creer un
#   septieme.
# - clear_recent_targets()/clear_all_targets() (2026-08-24) : simples
#   relais vers les commands homonymes, aucune confirmation ici — deja
#   geree cote ecran (screens/confirm.py) avant l'appel.
# Comment il sera utilise :
# - screens/request_panel.py, connection_panel.py, ramp_panel.py (les
#   trois lancements manuels), screens/history.py (relecture),
#   screens/settings_screen.py (purge des cibles).
#---------------------------------------------------------------------->
