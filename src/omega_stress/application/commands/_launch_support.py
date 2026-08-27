# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Assemblage partage par run_request_load.py, run_connection_load.py,
run_ramp_load.py et replay_run.py."""
from __future__ import annotations

from omega_stress.application.dto.mappers import run_to_dto
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.exceptions import CapabilityUnavailableError
from omega_stress.application.pipeline.executor import execute
from omega_stress.application.pipeline.guards.capability_guard import check_capability
from omega_stress.application.pipeline.guards.precheck_guard import check_precheck
from omega_stress.application.pipeline.hooks.audit_hook import AuditSink
from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.application.pipeline.planner import prepare_plan
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.validators import PlanValidationError
from omega_stress.domain.runs.models import LoadRun
from omega_stress.domain.targets.models import Target
from omega_stress.domain.targets.validation import parse_target_address
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import Clock, IdFactory

LaunchError = PlanValidationError | CapabilityUnavailableError


async def launch_plan(
    plan: LoadPlan,
    *,
    target_id: str,
    target_url: str,
    profile_id: str | None,
    requested_rate_per_minute: int | None,
    load_runner: LoadRunner,
    run_progress_notifier: RunProgressNotifier,
    run_repository: RunRepository,
    target_repository: TargetRepository,
    audit_sink: AuditSink,
    notification_sink: NotificationSink,
    id_factory: IdFactory,
    now: Clock,
    capability_registry: CapabilityRegistry | None = None,
    required_capability: str | None = None,
) -> Result[RunDTO, LaunchError]:
    """Verifie le pre-check et la capacite systeme, valide le plan, lance
    l'execution, PERSISTE le run termine et retourne son DTO.

    Ne verifie PAS l'autorisation de la cible : cette verification
    (application/pipeline/guards/authorization_guard.py) doit avoir lieu
    AVANT la construction du LoadPlan par l'appelant, puisque
    LoadPlan.target_authorization_confirmed doit deja porter le resultat
    reel de cette verification au moment ou ce plan est construit.
    """
    precheck_check = check_precheck(plan.level, precheck_validated=plan.precheck_validated)
    if isinstance(precheck_check, Err):
        return precheck_check

    if capability_registry is not None and required_capability is not None:
        capability_check = check_capability(
            required_capability, capability_registry=capability_registry
        )
        if isinstance(capability_check, Err):
            return capability_check

    prepared = prepare_plan(plan)
    if isinstance(prepared, Err):
        return prepared

    started_at = now()

    parsed_address = parse_target_address(target_url)
    if isinstance(parsed_address, Ok):
        target_repository.save_recent(
            Target(
                id=target_id,
                address=parsed_address.value,
                created_at=started_at,
                last_used_at=started_at,
            )
        )

    run = LoadRun(
        id=id_factory(),
        profile_id=profile_id,
        target_id=target_id,
        family=plan.family,
        level=plan.level,
        started_at=started_at,
    )

    finished = await execute(
        prepared.value,
        run=run,
        target_url=target_url,
        requested_rate_per_minute=requested_rate_per_minute,
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
# - Factorise la sequence commune aux quatre commands qui declenchent une
#   execution reelle (run_request_load, run_connection_load, run_ramp_load,
#   replay_run) : guard pre-check, guard capacite (optionnel), validation
#   finale du plan, construction du LoadRun initial, execution,
#   PERSISTANCE, mapping en RunDTO.
# Pourquoi dans application/commands/ (charte, ecart mineur assume) :
# - Fichier prefixe `_` (non liste dans l'arborescence initiale de
#   ARCHITECTURE.md §2) : aide interne au paquet commands/, jamais importe
#   en dehors de application/commands/ — evite de dupliquer 4 fois la
#   meme sequence guard/planner/executor/mapping. Symetrique a l'ajout de
#   theme_dto.py : un fichier en plus, pas une regle assouplie.
# Ce qu'il ne contient PAS :
# - Aucun guard d'autorisation (voir docstring de launch_plan : la
#   verification d'autorisation doit avoir lieu AVANT, cote appelant, car
#   elle determine le champ target_authorization_confirmed du LoadPlan
#   passe en parametre).
# - Aucune construction de LoadPlan (chaque command construit le sien,
#   avec sa propre famille/preset).
# Points cles :
# - now: Clock, pas datetime (2026-08-27, correction de bug reel : voir
#   shared/typing.py::Clock et application/pipeline/executor.py) :
#   `started_at = now()` est appele UNE FOIS ici (instant de depart,
#   reutilise pour started_at ET pour created_at/last_used_at de la
#   cible), puis le Clock est transmis TEL QUEL (pas appele) a execute(),
#   qui rappellera now() fraichement a la cloture — jamais la valeur de
#   depart reutilisee comme finished_at.
# - run_repository.save() est appele ICI, apres l'execution — correction
#   d'une premiere version de ce fichier qui laissait la persistance a
#   "l'appelant" alors que celui-ci ne recoit qu'un RunDTO (pas
#   l'entite LoadRun), rendant la persistance impossible en pratique
#   depuis interfaces/. Coherent avec le reste du projet : chaque command
#   persiste lui-meme via son port (voir create_profile.py, pin_target.py).
# - capability_registry/required_capability restent optionnels
#   (None par defaut) : infrastructure/probe/ n'est pas encore construit a
#   ce stade, donc aucun appelant ne peut fournir un registre reellement
#   peuple pour l'instant ; le guard de capacite reste branchable des que
#   ce sera le cas, sans reecrire ce fichier.
# - LaunchError = PlanValidationError | CapabilityUnavailableError est le
#   type d'erreur commun renvoye par les quatre commands appelants.
# - target_repository.save_recent() (2026-08-24) : AVANT ce correctif,
#   aucun appelant du projet n'appelait jamais save_recent() nulle part —
#   une cible lancee en mode manuel (jamais epinglee) n'etait donc JAMAIS
#   persistee, ce qui cassait deux choses en cascade : la liste des
#   "cibles recentes" (ports/target_repository.py::list_recent(), deja
#   consommee par application/queries/list_targets.py) restait toujours
#   vide, et replay_run.py echouait TOUJOURS avec "Cible introuvable" des
#   qu'un run manuel etait relance depuis un profil — meme une fois
#   profile_id correctement transmis (voir screens/request_panel.py et
#   consorts, meme jour). Erreur de parsing (parse_target_address) jamais
#   fatale ici : ce n'est qu'un enregistrement de confort, jamais une
#   condition de lancement (deja validee plus tot dans le pipeline reel
#   pour la cible elle-meme).
# - Cible deja epinglee/recente : save_recent() la reecrit quand meme
#   (memes id/adresse) — effet secondaire voulu, pas un bug : rafraichit
#   last_used_at a chaque nouveau lancement, coherent avec le sens du mot
#   "recente".
# Comment il sera utilise (apercu) :
# - application/commands/run_request_load.py, run_connection_load.py,
#   run_ramp_load.py, replay_run.py.
#---------------------------------------------------------------------->
