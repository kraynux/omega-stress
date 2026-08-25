# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : orchestre listage, creation et gel des profils."""
from __future__ import annotations

from omega_stress.application.commands.create_profile import create_profile
from omega_stress.application.commands.delete_profile import delete_profile as _delete_profile
from omega_stress.application.commands.freeze_profile import freeze_profile
from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.application.queries.list_profiles import list_profiles
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Result
from omega_stress.domain.errors import ValidationError
from omega_stress.interfaces.tui.presenters.profile_presenter import sorted_for_display
from omega_stress.ports.profile_repository import ProfileRepository
from omega_stress.shared.clock import utc_now
from omega_stress.shared.ids import new_id


def load_profiles(*, profile_repository: ProfileRepository) -> tuple[ProfileDTO, ...]:
    """Profils prets pour l'affichage (favoris d'abord, voir
    presenters/profile_presenter.py)."""
    return sorted_for_display(list_profiles(profile_repository=profile_repository))


def create(
    *,
    profile_repository: ProfileRepository,
    name: str,
    description: str,
    default_target_id: str,
    family: TestFamily,
    level: IntensityLevel,
    duration_minutes: int,
    max_error_rate: float,
    max_p95_latency_ms: float | None = None,
    tags: tuple[str, ...] = (),
    extended_duration_authorized: bool = False,
) -> Result[ProfileDTO, ValidationError]:
    """Cree un profil depuis l'assistant de creation (screens/profile_wizard.py)."""
    return create_profile(
        profile_repository=profile_repository,
        id_factory=new_id,
        now=utc_now(),
        name=name,
        description=description,
        default_target_id=default_target_id,
        family=family,
        level=level,
        duration_minutes=duration_minutes,
        max_error_rate=max_error_rate,
        max_p95_latency_ms=max_p95_latency_ms,
        tags=tags,
        extended_duration_authorized=extended_duration_authorized,
    )


def freeze(
    profile_id: str, *, profile_repository: ProfileRepository
) -> Result[ProfileDTO, ValidationError]:
    """Fige un profil existant (action "figer" de screens/profiles.py)."""
    return freeze_profile(profile_id, profile_repository=profile_repository, now=utc_now())


def delete(profile_id: str, *, profile_repository: ProfileRepository) -> None:
    """Supprime definitivement un profil (action "supprimer" de
    screens/profiles.py)."""
    _delete_profile(profile_id, profile_repository=profile_repository)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de screens/profiles.py et
#   screens/profile_wizard.py vers application/commands/ et
#   application/queries/ pour tout ce qui concerne les profils.
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - Fournit id_factory=new_id et now=utc_now() explicitement (jamais
#   passes par l'ecran lui-meme) : seul ce controller appelle
#   shared/ids.py et shared/clock.py pour le sous-domaine profils, comme
#   le fait interfaces/cli/commands/profile_command.py de son cote.
# Ce qu'il ne contient PAS :
# - Aucune regle de validation (deja dans domain/profiles/validation.py,
#   relayee telle quelle via le Result retourne).
# Points cles :
# - load_profiles() applique toujours le tri d'affichage : aucun ecran ne
#   doit appeler application/queries/list_profiles.py directement, pour
#   garder un seul point de tri.
# - delete() (2026-08-24) : simple relais vers le command homonyme,
#   aucune confirmation ici (deja geree cote ecran via screens/confirm.py
#   avant l'appel) — fige ou non, voir application/commands/
#   delete_profile.py pour la portee complete.
# Comment il sera utilise :
# - screens/profiles.py, screens/profile_wizard.py.
#---------------------------------------------------------------------->
