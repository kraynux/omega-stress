# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Validation structurelle d'un Profil (creation ou modification avant gel)."""
from __future__ import annotations

from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.load import policies
from omega_stress.domain.profiles.models import Profile


def validate_profile(profile: Profile) -> Result[Profile, ValidationError]:
    """Verifie qu'un profil est structurellement coherent avec les
    politiques de domain/load/ — ne verifie pas la joignabilite de la
    cible par defaut (role du pre-check, pas une regle de profil)."""
    if not profile.name.strip():
        return Err(ValidationError("Le nom du profil ne peut pas etre vide."))

    allowed = policies.allowed_durations_minutes(
        profile.level, extended_authorized=profile.extended_duration_authorized
    )
    if profile.duration.minutes not in allowed:
        return Err(
            ValidationError(
                f"Duree {profile.duration.minutes} min non autorisee pour le niveau "
                f"{profile.level.value} dans ce profil "
                f"(extended_duration_authorized={profile.extended_duration_authorized})."
            )
        )

    return Ok(profile)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Validation structurelle pure d'un Profil : nom non vide, duree
#   compatible avec le niveau d'intensite et l'autorisation etendue
#   portee par le profil lui-meme.
# Pourquoi dans domain/profiles/ (charte) :
# - Consomme domain/load/policies.py comme source de verite unique pour
#   les durees autorisees, ne duplique jamais les tuples de duree.
# Ce qu'il ne contient PAS :
# - Aucune verification de l'existence reelle de default_target_id (c'est
#   le role d'application/commands/create_profile.py, qui a acces au port
#   target_repository — un value object domain/profiles/models.py ne
#   verifie jamais une reference d'ID contre un stockage).
# - Aucune verification de pre-check ou d'autorisation de cible : ce sont
#   des regles evaluees au moment du LANCEMENT d'un run
#   (domain/load/validators.py::validate_plan), pas a la creation d'un
#   profil qui ne s'execute pas encore.
# Points cles :
# - extended_duration_authorized est lu depuis le profil lui-meme (pas
#   suppose depuis `frozen`) : voir domain/profiles/models.py pour la
#   justification de cette independance.
# Comment il sera utilise (apercu) :
# - application/commands/create_profile.py et freeze_profile.py appellent
#   validate_profile() avant toute persistance.
# - domain/profiles/service.py::freeze() l'appelle avant de figer.
#---------------------------------------------------------------------->
