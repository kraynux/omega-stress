# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : creer un profil de test."""
from __future__ import annotations

from datetime import datetime

from omega_stress.application.dto.mappers import profile_to_dto
from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.profiles.validation import validate_profile
from omega_stress.ports.profile_repository import ProfileRepository
from omega_stress.shared.typing import IdFactory


def create_profile(
    *,
    profile_repository: ProfileRepository,
    id_factory: IdFactory,
    now: datetime,
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
    """Cree un profil non fige. Le figer est une action separee (voir
    application/commands/freeze_profile.py)."""
    duration_result = Duration.for_level(
        level, duration_minutes, extended_authorized=extended_duration_authorized
    )
    if isinstance(duration_result, Err):
        return duration_result

    profile = Profile(
        id=id_factory(),
        name=name,
        description=description,
        default_target_id=default_target_id,
        family=family,
        level=level,
        duration=duration_result.value,
        thresholds=Thresholds(max_error_rate=max_error_rate, max_p95_latency_ms=max_p95_latency_ms),
        created_at=now,
        tags=tags,
        extended_duration_authorized=extended_duration_authorized,
    )

    validated = validate_profile(profile)
    if isinstance(validated, Err):
        return validated

    profile_repository.save(validated.value)
    return Ok(profile_to_dto(validated.value))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Assemble un Profile a partir de parametres primitifs, le valide, le
#   persiste, retourne son DTO.
# Pourquoi dans application/commands/ (charte) :
# - Orchestre domain/load/models.py::Duration.for_level(),
#   domain/profiles/validation.py::validate_profile() et le port
#   profile_repository — ne contient aucune regle metier propre (la
#   validite d'une duree ou d'un profil reste decidee par domain/).
# Ce qu'il ne contient PAS :
# - Aucune verification que default_target_id reference une cible
#   existante : deliberement absent en V1, faute d'exigence explicite du
#   plan produit a ce niveau (le panneau de tests selectionne une cible
#   deja existante via son propre picker, donc l'id est presume valide au
#   moment de la creation d'un profil) — a ajouter explicitement si un
#   besoin de validation croisee est confirme.
# - Aucun rendu (pas de formatage pour affichage) : le DTO retourne est
#   deja la forme la plus aplatie, la mise en forme finale reste a
#   interfaces/.
# Points cles :
# - Deux Result intermediaires (duration_result, validated) sont chacun
#   retournes tels quels en cas d'echec plutot que re-enveloppes : evite
#   de perdre le type d'erreur precis (ValidationError dans les deux cas
#   ici, mais le principe s'applique meme si les types divergent).
# - id_factory et now sont des parametres explicites (jamais un appel
#   direct a shared/ids.py ou shared/clock.py dans ce fichier) : rend le
#   command testable avec des valeurs deterministes.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/profile_wizard.py,
#   interfaces/cli/commands/profile_command.py.
#---------------------------------------------------------------------->
