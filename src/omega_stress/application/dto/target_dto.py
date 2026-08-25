# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""DTO expose a la presentation pour une Cible."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TargetDTO:
    """Vue plate d'une cible, epinglee ou recente."""

    id: str
    base_url: str
    tags: tuple[str, ...]
    notes: str
    pinned: bool
    last_used_at: str | None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Forme plate d'une cible (Target ou PinnedTarget), sans exposer
#   TargetAddress ni la distinction structurelle entre les deux entites
#   domaine.
# Pourquoi dans application/dto/ (charte) :
# - Objet de transfert : la presentation n'a pas besoin de savoir si la
#   source domaine etait un Target ou un PinnedTarget, seulement si
#   pinned est vrai.
# Ce qu'il ne contient PAS :
# - Aucun champ authorized_at/pinned_at distinct : `pinned=True` suffit a
#   la presentation (le detail temporel de l'epinglage n'a pas d'usage
#   d'affichage identifie en V1 au niveau de la liste de cibles).
# Points cles :
# - base_url reprend TargetAddress.base_url tel quel (deja une chaine
#   prete a l'affichage, pas de recomposition cote presentation).
# Comment il sera utilise (apercu) :
# - application/dto/mappers.py::target_to_dto() /
#   pinned_target_to_dto().
# - interfaces/tui/widgets/target_picker.py.
#---------------------------------------------------------------------->
