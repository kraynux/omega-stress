# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : lancer un Test requetes (debit)."""
from __future__ import annotations

from omega_stress.application.commands._launch_support import LaunchError, launch_plan
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.pipeline.guards.authorization_guard import check_authorization
from omega_stress.application.pipeline.hooks.audit_hook import AuditSink
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import DurationPresetId, IntensityLevel, TestFamily
from omega_stress.core.results import Err, Result
from omega_stress.domain.errors import UnauthorizedTargetError
from omega_stress.domain.load import policies
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.presets import fixed_rate_preset
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import Clock, IdFactory

_REQUIRED_CAPABILITY = "system.load_capacity"


async def run_request_load(
    *,
    target_id: str,
    target_url: str,
    level: IntensityLevel,
    duration_minutes: int,
    thresholds: Thresholds,
    explicit_confirmation: bool,
    precheck_validated: bool,
    target_repository: TargetRepository,
    load_runner: LoadRunner,
    run_progress_notifier: RunProgressNotifier,
    run_repository: RunRepository,
    audit_sink: AuditSink,
    notification_sink: NotificationSink,
    id_factory: IdFactory,
    now: Clock,
    profile_id: str | None = None,
    capability_registry: CapabilityRegistry | None = None,
    duration_preset_id: DurationPresetId | None = None,
    reinforced_confirmation_text: str | None = None,
    safety_mode: bool = True,
) -> Result[RunDTO, UnauthorizedTargetError | LaunchError]:
    """Lance un Test requetes en mode manuel borne (profile_id=None) ou
    depuis un profil deja converti par l'appelant (profile_id fourni pour
    tracabilite — le LoadPlan lui-meme est toujours reconstruit ici a
    partir des parametres explicites, jamais depuis un Profile).

    duration_preset_id (mode "profil" D1-D6, optionnel) : quand fourni,
    duration_minutes doit deja valoir duration_preset(duration_preset_id)
    .total_minutes (verifie par domain/load/validators.py::validate_plan()
    en aval, pas ici) — la validation manuelle (Duration.for_level) est
    alors sautee, remplacee par evaluate_duration_preset()."""
    authorization = check_authorization(
        target_id, target_repository=target_repository, explicit_confirmation=explicit_confirmation
    )
    if isinstance(authorization, Err):
        return authorization

    if duration_preset_id is not None:
        duration = Duration(minutes=duration_minutes)
    else:
        duration_result = Duration.for_level(
            level, duration_minutes, extended_authorized=precheck_validated
        )
        if isinstance(duration_result, Err):
            return duration_result
        duration = duration_result.value

    plan = LoadPlan(
        id=id_factory(),
        family=TestFamily.REQUEST,
        level=level,
        duration=duration,
        thresholds=thresholds,
        target_authorization_confirmed=True,
        precheck_validated=precheck_validated,
        duration_preset_id=duration_preset_id,
        reinforced_confirmation_text=reinforced_confirmation_text,
        safety_mode=safety_mode,
    )

    preset = fixed_rate_preset(level)
    return await launch_plan(
        plan,
        target_id=target_id,
        target_url=target_url,
        profile_id=profile_id,
        requested_rate_per_minute=preset.requests_per_minute,
        load_runner=load_runner,
        run_progress_notifier=run_progress_notifier,
        run_repository=run_repository,
        target_repository=target_repository,
        audit_sink=audit_sink,
        notification_sink=notification_sink,
        id_factory=id_factory,
        now=now,
        capability_registry=capability_registry,
        required_capability=(
            _REQUIRED_CAPABILITY if level in policies.PRECHECK_MANDATORY_LEVELS else None
        ),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Construit un LoadPlan de famille REQUEST a partir de parametres
#   explicites (mode manuel borne), puis delegue a
#   application/commands/_launch_support.py::launch_plan() pour le reste
#   de l'orchestration (pre-check, capacite, validation, execution).
# Pourquoi dans application/commands/ (charte) :
# - Verifie l'autorisation AVANT de construire le plan (voir docstring de
#   launch_plan() : cette verification doit preceder la construction pour
#   que target_authorization_confirmed soit truthful).
# Ce qu'il ne contient PAS :
# - Aucune construction de plan depuis un Profile fige : si l'appelant
#   part d'un profil, c'est a lui de le convertir au prealable
#   (domain/profiles/service.py::to_load_plan()) puis d'extraire les
#   valeurs necessaires — ce command ne prend que des primitives.
# - Aucune logique de guard/execution (voir _launch_support.py).
# Points cles :
# - required_capability n'est verifie que pour Violent/Maximum, la meme
#   source que la regle de pre-check obligatoire (domain/load/policies.py::
#   PRECHECK_MANDATORY_LEVELS, plus de tuple local duplique depuis
#   Phase 3) : les autres niveaux restent toujours disponibles sans
#   verification de capacite systeme supplementaire.
# - profile_id est un champ de tracabilite pur ici (transmis tel quel au
#   LoadRun cree) : ce command ne verifie jamais que le profil existe
#   reellement, cette verification reste du ressort de l'appelant s'il
#   part effectivement d'un profil.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/request_panel.py,
#   interfaces/cli/commands/run_command.py.
#---------------------------------------------------------------------->
