# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : lancer un Test connexions (simultaneite)."""
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
from omega_stress.domain.load.duration_presets import (
    build_duration_preset_ramp_steps,
    duration_preset,
)
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import Clock, IdFactory

_REQUIRED_CAPABILITY = "system.load_capacity"


async def run_connection_load(
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
    """Lance un Test connexions en mode manuel borne. Symetrique a
    run_request_load.py, seule differe la famille (CONNECTION) et
    l'absence de debit demande (la simultaneite n'a pas de notion de
    requetes/minute, voir domain/load/presets.py::FixedRatePreset).

    duration_preset_id (mode "profil" D1-D6, optionnel) : peuple aussi
    ramp_steps (domain/load/duration_presets.py::
    build_duration_preset_ramp_steps()) — seule famille hors RAMP a le
    faire, autorise explicitement par domain/load/validators.py::
    validate_plan() dans ce cas precis (voir infrastructure/runner/
    engine_params.py, branche CONNECTION desormais phase-aware)."""
    authorization = check_authorization(
        target_id, target_repository=target_repository, explicit_confirmation=explicit_confirmation
    )
    if isinstance(authorization, Err):
        return authorization

    if duration_preset_id is not None:
        duration = Duration(minutes=duration_minutes)
        ramp_steps = build_duration_preset_ramp_steps(duration_preset(duration_preset_id))
    else:
        duration_result = Duration.for_level(
            level, duration_minutes, extended_authorized=precheck_validated
        )
        if isinstance(duration_result, Err):
            return duration_result
        duration = duration_result.value
        ramp_steps = ()

    plan = LoadPlan(
        id=id_factory(),
        family=TestFamily.CONNECTION,
        level=level,
        duration=duration,
        thresholds=thresholds,
        target_authorization_confirmed=True,
        precheck_validated=precheck_validated,
        ramp_steps=ramp_steps,
        duration_preset_id=duration_preset_id,
        reinforced_confirmation_text=reinforced_confirmation_text,
        safety_mode=safety_mode,
    )

    return await launch_plan(
        plan,
        target_id=target_id,
        target_url=target_url,
        profile_id=profile_id,
        requested_rate_per_minute=None,
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
# - Meme structure que run_request_load.py, adaptee au Test connexions :
#   famille CONNECTION, aucun debit demande transmis a l'executeur.
# Pourquoi dans application/commands/ (charte) :
# - Fichier distinct plutot qu'un parametre "family" sur un command
#   generique unique : coherent avec la convention de nommage
#   (ARCHITECTURE.md §6, un fichier par famille de test) et avec le
#   principe qu'aucune regle metier ne doit exister dans un command sans
#   exister, de la meme facon, dans les autres adaptateurs de
#   presentation qui l'appellent.
# Ce qu'il ne contient PAS :
# - Aucun debit demande (requested_rate_per_minute=None) : contrairement
#   a run_request_load.py, un Test connexions n'a pas de notion de
#   goulot d'etranglement basee sur un debit — la capacite du systeme a
#   tenir N connexions simultanees n'est pas mesuree par ce mecanisme en
#   V1 (voir domain/load/presets.py::FixedRatePreset.concurrent_connections,
#   non consomme par degraded_mode.py).
# Points cles :
# - Identique a run_request_load.py pour l'autorisation, la duree et la
#   verification de capacite : seule la famille et le debit demande
#   different.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/connection_panel.py,
#   interfaces/cli/commands/run_command.py.
#---------------------------------------------------------------------->
