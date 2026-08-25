# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""DTO expose a la presentation pour l'etat du terminal detecte."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TerminalStatusDTO:
    """Vue plate du resultat de detection + decision de profil de rendu."""

    family: str
    columns: int
    rows: int
    render_profile: str

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Forme plate combinant TerminalSignals et le RenderProfile decide,
#   prete pour l'affichage (badge, ecran d'avertissement).
# Pourquoi dans application/dto/ (charte) :
# - Objet de transfert : la presentation ne recoit ni TerminalSignals ni
#   TerminalProfile (domain/terminal/models.py) directement.
# Ce qu'il ne contient PAS :
# - Aucun champ is_ssh : non utilise par l'affichage en V1 (seul le
#   profil de rendu final compte pour l'utilisateur), a ajouter si un
#   besoin d'affichage reel apparait plutot que par anticipation.
# Points cles :
# - render_profile est deja la chaine `.value` de l'enum RenderProfile,
#   pas l'enum lui-meme.
# Comment il sera utilise (apercu) :
# - application/dto/mappers.py::terminal_profile_to_dto().
# - interfaces/tui/screens/terminal_warning.py,
#   interfaces/tui/widgets/render_profile_badge.py.
#---------------------------------------------------------------------->
