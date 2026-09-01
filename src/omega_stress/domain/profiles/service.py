# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regles metier du sous-domaine profiles : gel, duplication, conversion en plan."""
from __future__ import annotations

from datetime import datetime

from omega_stress.core.enums import TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.profiles.validation import validate_profile


def freeze(profile: Profile, *, now: datetime) -> Result[Profile, ValidationError]:
    """Fige un profil : devient immuable au sens produit, reutilisable tel
    quel dans l'historique et pour relancer un test. Un profil deja fige
    ne peut pas etre refige (retourne le profil inchange sans erreur : le
    gel est idempotent, pas une erreur de repeter l'action)."""
    if profile.frozen:
        return Ok(profile)

    validated = validate_profile(profile)
    if isinstance(validated, Err):
        return validated

    return Ok(
        Profile(
            id=profile.id,
            name=profile.name,
            description=profile.description,
            default_target_id=profile.default_target_id,
            family=profile.family,
            level=profile.level,
            duration=profile.duration,
            thresholds=profile.thresholds,
            created_at=profile.created_at,
            tags=profile.tags,
            extended_duration_authorized=profile.extended_duration_authorized,
            frozen=True,
            frozen_at=now,
            favorite=profile.favorite,
            archived=profile.archived,
        )
    )


def duplicate(profile: Profile, *, new_id: str, now: datetime) -> Profile:
    """Duplique un profil (fige ou non) en un nouveau profil non fige et
    non archive, reutilisable independamment de l'original."""
    return Profile(
        id=new_id,
        name=f"{profile.name} (copie)",
        description=profile.description,
        default_target_id=profile.default_target_id,
        family=profile.family,
        level=profile.level,
        duration=profile.duration,
        thresholds=profile.thresholds,
        created_at=now,
        tags=profile.tags,
        extended_duration_authorized=profile.extended_duration_authorized,
        frozen=False,
        frozen_at=None,
        favorite=False,
        archived=False,
    )


def to_load_plan(
    profile: Profile,
    *,
    plan_id: str,
    target_authorization_confirmed: bool,
    precheck_validated: bool = False,
) -> LoadPlan:
    """Convertit un profil (fige ou non) en LoadPlan pret a etre valide
    (domain/load/validators.py::validate_plan) puis execute. Les etapes de
    rampe sont derivees automatiquement pour un profil de famille RAMP —
    jamais stockees sur le profil lui-meme (voir domain/profiles/models.py).
    Mises a l'echelle de profile.duration.minutes (2026-09-01, meme
    correctif que application/commands/run_ramp_load.py, voir domain/
    load/builders.py::build_ramp_steps() pour le diagnostic complet)."""
    ramp_steps = (
        build_ramp_steps(profile.level, duration_minutes=profile.duration.minutes)
        if profile.family is TestFamily.RAMP
        else ()
    )
    return LoadPlan(
        id=plan_id,
        family=profile.family,
        level=profile.level,
        duration=profile.duration,
        thresholds=profile.thresholds,
        target_authorization_confirmed=target_authorization_confirmed,
        precheck_validated=precheck_validated,
        ramp_steps=ramp_steps,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - freeze() : fige un profil valide, idempotent si deja fige.
# - duplicate() : cree une copie independante non figee.
# - to_load_plan() : traduit un profil en LoadPlan executable, en derivant
#   les etapes de rampe pour les profils de famille RAMP.
# Pourquoi dans domain/profiles/ (charte) :
# - Orchestration de plusieurs entites/VO du meme sous-domaine (et de
#   domain/load/, meme couche) sans aucune I/O.
# Ce qu'il ne contient PAS :
# - Aucune persistance : freeze()/duplicate()/to_load_plan() retournent
#   des objets en memoire, la sauvegarde reste le role
#   d'infrastructure/storage/sqlite/profile_repository.py.
# - Aucune resolution de target_authorization_confirmed depuis un
#   repository : ce booleen est toujours fourni par l'appelant
#   (application/commands/run_*.py), qui seul a acces au port
#   target_repository pour verifier si la cible par defaut du profil est
#   epinglee-autorisee.
# Points cles :
# - freeze() utilise isinstance(validated, Err) plutot que .is_err pour un
#   narrowing de type correct avec mypy (validated: Result[Profile,
#   ValidationError] devient Err[ValidationError] dans la branche).
# - to_load_plan() ne re-valide pas le plan produit (duree, autorisation,
#   pre-check) : c'est le role de domain/load/validators.py::validate_plan,
#   toujours appele juste apres par l'application avant tout lancement.
# Comment il sera utilise (apercu) :
# - application/commands/freeze_profile.py appelle freeze().
# - application/commands/run_request_load.py (et connection/ramp)
#   appellent to_load_plan() puis domain/load/validators.py::validate_plan()
#   avant de passer au pipeline.
#---------------------------------------------------------------------->
