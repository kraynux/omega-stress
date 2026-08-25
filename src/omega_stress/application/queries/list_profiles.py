# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Query : lister les profils."""
from __future__ import annotations

from omega_stress.application.dto.mappers import profile_to_dto
from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.ports.profile_repository import ProfileRepository


def list_profiles(
    *, profile_repository: ProfileRepository, include_archived: bool = False
) -> tuple[ProfileDTO, ...]:
    """Liste les profils, en excluant les profils archives par defaut."""
    profiles = profile_repository.list_all()
    if not include_archived:
        profiles = tuple(p for p in profiles if not p.archived)
    return tuple(profile_to_dto(p) for p in profiles)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Query en lecture seule, sans effet de bord : recupere les profils via
#   le port et les convertit en ProfileDTO.
# Pourquoi dans application/queries/ (charte) :
# - Aucune modification d'etat, distinct des application/commands/.
# Ce qu'il ne contient PAS :
# - Aucune logique de tri specifique (l'ordre retourne suit celui du
#   repository) : un tri d'affichage (favoris d'abord, etc.) reste du
#   ressort de interfaces/tui/presenters/profile_presenter.py.
# Points cles :
# - include_archived=False par defaut : coherent avec le parcours normal
#   ("Profils" du menu principal), qui ne doit pas presenter les profils
#   archives sans action explicite de l'utilisateur.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/profile_controller.py,
#   interfaces/cli/commands/profile_command.py.
#---------------------------------------------------------------------->
