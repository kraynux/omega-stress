# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : rejouer un run existant, a partir de son profil fige."""
from __future__ import annotations

from omega_stress.application.commands._launch_support import LaunchError, launch_plan
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.pipeline.guards.authorization_guard import check_authorization
from omega_stress.application.pipeline.hooks.audit_hook import AuditSink
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Result
from omega_stress.domain.errors import UnauthorizedTargetError, ValidationError
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.presets import fixed_rate_preset, ramp_preset
from omega_stress.domain.profiles.service import to_load_plan
from omega_stress.domain.runs.validators import can_be_replayed
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.profile_repository import ProfileRepository
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import Clock, IdFactory

_HIGH_INTENSITY_LEVELS = (IntensityLevel.HAUT, IntensityLevel.MAXIMUM)
_REQUIRED_CAPABILITY = "system.load_capacity"


def _requested_rate_for(plan: LoadPlan) -> int | None:
    if plan.family is TestFamily.CONNECTION:
        return None
    if plan.family is TestFamily.RAMP:
        return ramp_preset(plan.level).peak_requests_per_minute
    return fixed_rate_preset(plan.level).requests_per_minute


async def replay_run(
    run_id: str,
    *,
    run_repository: RunRepository,
    profile_repository: ProfileRepository,
    target_repository: TargetRepository,
    load_runner: LoadRunner,
    run_progress_notifier: RunProgressNotifier,
    audit_sink: AuditSink,
    notification_sink: NotificationSink,
    id_factory: IdFactory,
    explicit_confirmation: bool,
    precheck_validated: bool,
    now: Clock,
    capability_registry: CapabilityRegistry | None = None,
) -> Result[RunDTO, ValidationError | UnauthorizedTargetError | LaunchError]:
    """Relance un run existant en reconstruisant son plan depuis le
    PROFIL FIGE qu'il reference (pas depuis les champs bruts de l'ancien
    run), contre la meme cible que l'execution originale
    (LoadRun.target_id) — pas la cible par defaut ACTUELLE du profil, qui
    a pu changer depuis (voir Points cles)."""
    run = run_repository.get(run_id)
    if run is None:
        return Err(ValidationError(f"Run {run_id!r} introuvable."))
    if not can_be_replayed(run):
        return Err(
            ValidationError(
                f"Le run {run_id!r} ne reference aucun profil et ne peut pas etre rejoue."
            )
        )

    profile = profile_repository.get(run.profile_id)  # type: ignore[arg-type]
    if profile is None:
        return Err(
            ValidationError(f"Profil {run.profile_id!r} introuvable, impossible de rejouer ce run.")
        )

    target = target_repository.get(run.target_id)
    if target is None:
        return Err(
            ValidationError(f"Cible {run.target_id!r} introuvable, impossible de rejouer ce run.")
        )

    authorization = check_authorization(
        run.target_id,
        target_repository=target_repository,
        explicit_confirmation=explicit_confirmation,
    )
    if isinstance(authorization, Err):
        return authorization

    plan = to_load_plan(
        profile,
        plan_id=id_factory(),
        target_authorization_confirmed=True,
        precheck_validated=precheck_validated,
    )

    return await launch_plan(
        plan,
        target_id=run.target_id,
        target_url=target.address.base_url,
        profile_id=profile.id,
        requested_rate_per_minute=_requested_rate_for(plan),
        load_runner=load_runner,
        run_progress_notifier=run_progress_notifier,
        run_repository=run_repository,
        target_repository=target_repository,
        audit_sink=audit_sink,
        notification_sink=notification_sink,
        id_factory=id_factory,
        now=now,
        capability_registry=capability_registry,
        required_capability=_REQUIRED_CAPABILITY if plan.level in _HIGH_INTENSITY_LEVELS else None,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Reconstruit un LoadPlan a partir du profil fige reference par un run
#   existant, puis reutilise application/commands/_launch_support.py::
#   launch_plan() comme les trois commands run_*_load.
# Pourquoi dans application/commands/ (charte) :
# - Orchestre run_repository, profile_repository, target_repository et
#   domain/profiles/service.py::to_load_plan(), sans regle metier propre :
#   toute la logique de conversion profil -> plan reste dans domain/.
# Ce qu'il ne contient PAS :
# - Aucune reconstruction depuis les champs bruts de l'ancien LoadRun
#   (niveau, famille...) : ceux-ci sont deja portes par le PROFIL, source
#   de verite unique pour "quoi relancer" — le run original ne sert qu'a
#   identifier CE profil et CETTE cible.
# Points cles :
# - _requested_rate_for() duplique la logique de choix de preset deja
#   presente separement dans chacun des trois commands run_*_load : reste
#   locale a ce fichier (pas promue en fonction partagee) car c'est le
#   seul command qui doit choisir CE preset dynamiquement depuis un
#   plan.family decouvert a l'execution, plutot que de le savoir d'avance
#   comme les trois autres.
# - Utilise run.target_id (la cible EFFECTIVEMENT visee par l'execution
#   originale), jamais profile.default_target_id : rejouer doit reproduire
#   ce qui s'est reellement passe, pas ce que le profil pointe aujourd'hui
#   par defaut.
# - precheck_validated reste un parametre fourni par l'appelant (pas
#   recalcule depuis un historique de Pre-check anterieur) : meme
#   simplification assumee que pour les trois commands run_*_load.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/history.py (action "relancer"),
#   interfaces/cli/commands/history_command.py.
#---------------------------------------------------------------------->
