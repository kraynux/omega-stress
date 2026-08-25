# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : figer un profil existant."""
from __future__ import annotations

from datetime import datetime

from omega_stress.application.dto.mappers import profile_to_dto
from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.profiles.service import freeze
from omega_stress.ports.profile_repository import ProfileRepository


def freeze_profile(
    profile_id: str, *, profile_repository: ProfileRepository, now: datetime
) -> Result[ProfileDTO, ValidationError]:
    """Fige un profil existant et persiste le resultat. Retourne
    ValidationError si le profil n'existe pas — reutilise ce type plutot
    qu'introduire une exception "NotFound" dediee, l'effet cote appelant
    (afficher un message, refuser l'action) etant identique."""
    profile = profile_repository.get(profile_id)
    if profile is None:
        return Err(ValidationError(f"Profil {profile_id!r} introuvable."))

    frozen = freeze(profile, now=now)
    if isinstance(frozen, Err):
        return frozen

    profile_repository.save(frozen.value)
    return Ok(profile_to_dto(frozen.value))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Recupere un profil existant, delegue le gel a
#   domain/profiles/service.py::freeze(), persiste, retourne le DTO.
# Pourquoi dans application/commands/ (charte) :
# - Orchestre repository + service domaine, sans regle metier propre (la
#   regle "un profil deja fige n'est pas refige" vit dans
#   domain/profiles/service.py::freeze(), pas ici).
# Ce qu'il ne contient PAS :
# - Aucune logique de gel elle-meme (deja dans domain/profiles/service.py).
# Points cles :
# - profile_id introuvable retourne un Err(ValidationError) plutot qu'une
#   exception ou None silencieux : coherent avec le fait qu'un command
#   (par opposition a une query) doit toujours renvoyer un Result
#   explicite pour toute issue possible.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/profiles.py (action "figer"),
#   interfaces/cli/commands/profile_command.py.
#---------------------------------------------------------------------->
