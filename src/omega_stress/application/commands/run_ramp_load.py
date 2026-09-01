# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : lancer un Test charge (montee progressive)."""
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
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.duration_presets import (
    build_duration_preset_ramp_steps,
    duration_preset,
)
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.presets import ramp_preset
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import Clock, IdFactory

_REQUIRED_CAPABILITY = "system.load_capacity"


async def run_ramp_load(
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
    """Lance un Test charge en mode manuel borne. Seule famille qui derive
    des etapes de rampe (domain/load/builders.py::build_ramp_steps) et
    dont le debit demande pour le calcul de goulot d'etranglement est le
    pic de la rampe (RampPreset.peak_requests_per_minute), pas un palier
    fixe.

    duration_preset_id (mode "profil" D1-D6, optionnel) : les ramp_steps
    proviennent alors de domain/load/duration_presets.py::
    build_duration_preset_ramp_steps() (4 phases) plutot que de
    build_ramp_steps() (2 phases, mode manuel)."""
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
        ramp_steps = build_ramp_steps(level, duration_minutes=duration_minutes)

    plan = LoadPlan(
        id=id_factory(),
        family=TestFamily.RAMP,
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

    preset = ramp_preset(level)
    return await launch_plan(
        plan,
        target_id=target_id,
        target_url=target_url,
        profile_id=profile_id,
        requested_rate_per_minute=preset.peak_requests_per_minute,
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
# - Meme structure que run_request_load.py, adaptee au Test charge :
#   famille RAMP, ramp_steps derives via domain/load/builders.py, debit
#   demande = pic de la rampe.
# Pourquoi dans application/commands/ (charte) :
# - Seul command qui appelle domain/load/builders.py::build_ramp_steps() :
#   les deux autres commands run_*_load laissent ramp_steps a son defaut
#   vide (), coherent avec la regle de domain/load/validators.py::
#   validate_plan() ("seul un Test charge peut definir des etapes de
#   rampe").
# Ce qu'il ne contient PAS :
# - Aucune duree de plateau configurable : entierement derivee par
#   build_ramp_steps() depuis le niveau (voir son propre commentaire INFO
#   DEV pour l'interpretation retenue sur la borne de plateau).
# Points cles :
# - duration_minutes recu ici reste la duree TOTALE bornee du panneau de
#   test (le meme choix ferme que les deux autres familles), transmise a
#   build_ramp_steps() (mode manuel) pour qu'elle RECALCULE ramp_up/
#   plateau proportionnellement (2026-09-01, bug reel corrige : avant ce
#   correctif, ces deux notions de duree n'etaient jamais reconciliees —
#   voir domain/load/builders.py::build_ramp_steps(), INFO DEV, pour le
#   diagnostic complet). En mode profil D1-D6, la reconciliation est deja
#   assuree autrement par build_duration_preset_ramp_steps() (warmup/
#   rampe/plateau/retour au calme exprimes en fractions de preset.
#   total_minutes des sa premiere version, jamais affectee par ce bug).
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/ramp_panel.py,
#   interfaces/cli/commands/run_command.py.
#---------------------------------------------------------------------->
