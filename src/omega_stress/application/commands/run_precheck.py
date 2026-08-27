# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : lancer un Pre-check (verification de sante cible, courte,
a intensite tres faible)."""
from __future__ import annotations

from omega_stress.application.dto.mappers import run_to_dto
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.pipeline.executor import execute
from omega_stress.application.pipeline.guards.authorization_guard import check_authorization
from omega_stress.application.pipeline.hooks.audit_hook import AuditSink
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.application.pipeline.planner import prepare_plan
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.validators import PlanValidationError
from omega_stress.domain.runs.models import LoadRun
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import Clock, IdFactory


async def run_precheck(
    *,
    target_id: str,
    target_url: str,
    target_repository: TargetRepository,
    load_runner: LoadRunner,
    run_progress_notifier: RunProgressNotifier,
    run_repository: RunRepository,
    audit_sink: AuditSink,
    notification_sink: NotificationSink,
    id_factory: IdFactory,
    explicit_confirmation: bool,
    now: Clock,
) -> Result[RunDTO, PlanValidationError]:
    """Lance un Pre-check : duree fixe de 1 minute (borne haute de la
    plage "30 secondes a 1 minute" du plan produit — voir Points cles),
    intensite Bas (la plus faible du catalogue de presets). Un Pre-check
    n'exige jamais son propre Pre-check prealable (domain/load/policies.py::
    is_precheck_mandatory(BAS) est toujours False), mais exige toujours
    l'autorisation de la cible comme n'importe quel run.
    """
    authorization = check_authorization(
        target_id, target_repository=target_repository, explicit_confirmation=explicit_confirmation
    )
    if isinstance(authorization, Err):
        return authorization

    plan = LoadPlan(
        id=id_factory(),
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=1.0),
        target_authorization_confirmed=True,
        precheck_validated=True,
    )

    prepared = prepare_plan(plan)
    if isinstance(prepared, Err):
        return prepared

    run = LoadRun(
        id=id_factory(),
        profile_id=None,
        target_id=target_id,
        family=plan.family,
        level=plan.level,
        started_at=now(),
        is_precheck=True,
    )

    finished = await execute(
        prepared.value,
        run=run,
        target_url=target_url,
        requested_rate_per_minute=None,
        load_runner=load_runner,
        run_progress_notifier=run_progress_notifier,
        audit_sink=audit_sink,
        notification_sink=notification_sink,
        now=now,
    )
    run_repository.save(finished)
    return Ok(run_to_dto(finished, target_address=target_url))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Assemble et execute le plan fixe d'un Pre-check (voir plan produit,
#   section Pre-check), sans passer par le helper launch_plan()
#   generique : un Pre-check ne construit jamais son LoadRun via ce
#   helper car il doit forcer is_precheck=True, que launch_plan() ne
#   parametre pas (choix delibere, voir _launch_support.py).
# Pourquoi dans application/commands/ (charte) :
# - Orchestre authorization_guard, planner, executor — memes briques que
#   les trois autres commands run_*_load, mais avec un plan entierement
#   fixe (aucun parametre de niveau/duree/seuils accepte de l'appelant).
# Ce qu'il ne contient PAS :
# - Aucun parametre level/duration_minutes/thresholds : contrairement aux
#   trois autres commands run_*_load, un Pre-check n'est PAS configurable
#   par l'utilisateur — ses valeurs sont figees par le plan produit.
# - Aucune verification de pre-check_guard sur lui-meme : BAS n'exige
#   jamais de pre-check (domain/load/policies.py::PRECHECK_MANDATORY_LEVELS
#   ne contient que HAUT/MAXIMUM), donc appeler ce guard serait un
#   contournement vide de sens.
# - Aucun calcul de validite temporelle d'un Pre-check anterieur (voir
#   domain/load/policies.py::PRECHECK_VALIDITY_HOURS, pas encore consomme
#   par un service dedie — deliberement differe, voir son propre
#   commentaire INFO DEV).
# Points cles :
# - now: Clock, pas datetime (2026-08-27, correction de bug reel : voir
#   shared/typing.py::Clock et application/pipeline/executor.py) :
#   started_at=now() capture l'instant de depart ; execute() recoit le
#   Clock tel quel et appelle now() a nouveau, fraichement, pour
#   finished_at une fois la minute de Pre-check ecoulee — jamais la meme
#   valeur figee pour les deux.
# - Duration(minutes=1) : le plan produit donne un intervalle ("30
#   secondes a 1 minute"), pas une valeur unique. La borne haute est
#   retenue ici pour reutiliser tel quel le value object Duration
#   (minutes entieres) sans introduire de granularite en secondes juste
#   pour ce cas — interpretation documentee, a revoir si un besoin de
#   precision sous la minute est confirme.
# - requested_rate_per_minute=None passe a execute() : un Pre-check n'a
#   pas de debit cible a comparer (pas de notion de goulot d'etranglement
#   pertinente sur une verification aussi courte).
# - Le run resultant porte is_precheck=True (domain/runs/models.py),
#   permettant de le distinguer des runs des trois familles principales
#   dans l'historique.
# - run_repository.save() est appele apres l'execution : ce command
#   persiste lui-meme son resultat, comme tous les autres commands (voir
#   application/commands/_launch_support.py::launch_plan(), meme
#   principe).
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/request_panel.py (et equivalents) declenchent
#   ce command avant d'autoriser un lancement Haut/Maximum.
# - interfaces/cli/commands/run_command.py, sous-commande precheck.
#---------------------------------------------------------------------->
