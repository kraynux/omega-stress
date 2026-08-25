# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : catalogue de themes et libelle d'etat pour l'ecran Reglages."""
from __future__ import annotations

from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.domain.theme.policies import TUI_THEMES


def available_theme_names() -> tuple[str, ...]:
    """Noms des themes selectionnables, dans l'ordre stable du catalogue
    (voir plan produit, ecran "Reglages" : liste des 10 themes TUI)."""
    return tuple(TUI_THEMES.keys())


def status_label(status: ThemeStatusDTO) -> str:
    """Libelle humain de l'etat de theme applique, mentionnant un
    eventuel repli (nom demande inconnu -> nom effectivement applique)."""
    if status.fell_back_from is None:
        return status.theme_name
    return f"{status.theme_name} (repli depuis {status.fell_back_from})"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Expose le catalogue de noms de themes (domain/theme/policies.py) sous
#   une forme directement utilisable par un ecran de selection, et met en
#   forme le repli eventuel d'un ThemeStatusDTO.
# Pourquoi dans interfaces/tui/presenters/ (charte) :
# - Lit TUI_THEMES en lecture seule (juste les noms) sans jamais
#   construire de Theme Textual ici (cela reste le role exclusif de
#   rendering/textual_theme_builder.py, seul module a importer `textual`
#   dans ce module ET a manipuler Palette directement).
# Ce qu'il ne contient PAS :
# - Aucune palette ni couleur : ce presenter ne manipule que des noms de
#   themes (str), jamais un objet Palette.
# Points cles :
# - available_theme_names() suit l'ordre d'insertion du dict TUI_THEMES
#   (garanti par Python 3.7+), lui-meme dans l'ordre de Projet/themes.txt
#   : ordre stable et intentionnel, pas un tri alphabetique.
# Comment il sera utilise :
# - screens/settings_screen.py (liste des themes proposes),
#   widgets/theme_badge.py (libelle du theme actif).
#---------------------------------------------------------------------->
