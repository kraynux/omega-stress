# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : lancer un Test charge (montee progressive)."""
from __future__ import annotations

from datetime import datetime

from omega_stress.application.commands._launch_support import LaunchError, launch_plan
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.pipeline.guards.authorization_guard import check_authorization
from omega_stress.application.pipeline.hooks.audit_hook import AuditSink
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Result
from omega_stress.domain.errors import UnauthorizedTargetError
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.presets import ramp_preset
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import IdFactory

_HIGH_INTENSITY_LEVELS = (IntensityLevel.HAUT, IntensityLevel.MAXIMUM)
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
    now: datetime,
    profile_id: str | None = None,
    capability_registry: CapabilityRegistry | None = None,
) -> Result[RunDTO, UnauthorizedTargetError | LaunchError]:
    """Lance un Test charge en mode manuel borne. Seule famille qui derive
    des etapes de rampe (domain/load/builders.py::build_ramp_steps) et
    dont le debit demande pour le calcul de goulot d'etranglement est le
    pic de la rampe (RampPreset.peak_requests_per_minute), pas un palier
    fixe."""
    authorization = check_authorization(
        target_id, target_repository=target_repository, explicit_confirmation=explicit_confirmation
    )
    if isinstance(authorization, Err):
        return authorization

    duration_result = Duration.for_level(
        level, duration_minutes, extended_authorized=precheck_validated
    )
    if isinstance(duration_result, Err):
        return duration_result

    plan = LoadPlan(
        id=id_factory(),
        family=TestFamily.RAMP,
        level=level,
        duration=duration_result.value,
        thresholds=thresholds,
        target_authorization_confirmed=True,
        precheck_validated=precheck_validated,
        ramp_steps=build_ramp_steps(level),
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
        required_capability=_REQUIRED_CAPABILITY if level in _HIGH_INTENSITY_LEVELS else None,
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
#   test (le meme choix ferme que les deux autres familles) ; elle n'est
#   pas recalculee a partir de la somme ramp_up + plateau des
#   RampStep — ce sont deux notions de duree paralleles en V1 (l'une
#   gouverne le choix utilisateur ferme, l'autre la forme reelle de la
#   rampe), non reconciliees explicitement faute d'exigence du plan
#   produit sur ce point precis.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/ramp_panel.py,
#   interfaces/cli/commands/run_command.py.
#---------------------------------------------------------------------->
