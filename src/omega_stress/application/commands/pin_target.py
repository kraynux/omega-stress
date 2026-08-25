# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : epingler une cible, avec confirmation d'autorisation."""
from __future__ import annotations

from datetime import datetime

from omega_stress.application.dto.mappers import pinned_target_to_dto
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import UnauthorizedTargetError, ValidationError
from omega_stress.domain.targets.models import Target
from omega_stress.domain.targets.service import pin
from omega_stress.domain.targets.validation import parse_target_address
from omega_stress.ports.target_repository import TargetRepository
from omega_stress.shared.typing import IdFactory


def pin_target(
    *,
    target_repository: TargetRepository,
    id_factory: IdFactory,
    now: datetime,
    raw_address: str,
    authorization_confirmed: bool,
    tags: tuple[str, ...] = (),
    notes: str = "",
) -> Result[TargetDTO, ValidationError | UnauthorizedTargetError]:
    """Parse l'adresse saisie, construit une cible, l'epingle (exige la
    confirmation d'autorisation, ARCHITECTURE.md §7) et persiste."""
    address_result = parse_target_address(raw_address)
    if isinstance(address_result, Err):
        return address_result

    target = Target(
        id=id_factory(), address=address_result.value, created_at=now, tags=tags, notes=notes
    )

    pinned_result = pin(target, authorization_confirmed=authorization_confirmed, now=now)
    if isinstance(pinned_result, Err):
        return pinned_result

    target_repository.save_pinned(pinned_result.value)
    return Ok(pinned_target_to_dto(pinned_result.value))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Enchaine parsing d'adresse (domain/targets/validation.py), construction
#   d'un Target, epinglage (domain/targets/service.py::pin()) et
#   persistance.
# Pourquoi dans application/commands/ (charte) :
# - Orchestration pure, aucune regle metier propre : la regle
#   d'autorisation reste entierement dans domain/targets/service.py::pin().
# Ce qu'il ne contient PAS :
# - Aucune verification de joignabilite reseau de la cible (role du
#   pre-check, application/commands/run_precheck.py — a venir avec le
#   pipeline).
# - Aucun contournement de la confirmation d'autorisation : ce command ne
#   peut pas epingler sans authorization_confirmed=True, quel que soit
#   l'appelant (TUI ou CLI) — verifie cote domaine, pas seulement ici.
# Points cles :
# - Le type de retour Result[TargetDTO, ValidationError |
#   UnauthorizedTargetError] rend explicite les deux familles d'echec
#   possibles (adresse mal formee vs autorisation refusee), sans les
#   fondre dans un DomainError generique.
# Comment il sera utilise (apercu) :
# - interfaces/tui/widgets/target_picker.py (via
#   authorization_checkbox.py), interfaces/cli/commands/run_command.py
#   pour une cible non deja epinglee.
#---------------------------------------------------------------------->
