# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : catalogue de themes et libelle d'etat pour l'ecran Reglages."""
from __future__ import annotations

from omega_lib.theme.policies import EXPORT_PALETTES, TUI_THEMES

from omega_stress.application.dto.theme_dto import ThemeStatusDTO


def available_theme_names() -> tuple[str, ...]:
    """Noms des themes selectionnables, dans l'ordre stable du catalogue
    (voir plan produit, ecran "Reglages" : liste des 10 themes TUI)."""
    return tuple(TUI_THEMES.keys())


def available_export_theme_names() -> tuple[str, ...]:
    """Noms des themes d'export HTML selectionnables (catalogue
    EXPORT_PALETTES, independant de TUI_THEMES, voir domain/theme/
    policies.py et son INFO DEV). A utiliser pour tout Select de theme
    d'export (screens/export_dialog.py) : les 10 noms de
    available_theme_names() ne correspondent PAS tous a un theme d'export
    valide (validate_export_job() les rejetterait), et les themes
    export-only (light-basic, light-alt) n'apparaissent que via cette
    fonction."""
    return tuple(EXPORT_PALETTES.keys())


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
# - available_export_theme_names() (2026-08-27, correction de bug reel :
#   screens/export_dialog.py peuplait son Select de theme d'export avec
#   available_theme_names() — catalogue TUI_THEMES, 10 noms — au lieu du
#   catalogue EXPORT_PALETTES, 5 noms. Consequence : 7 noms proposes
#   (omega-dark/light/pink/hack/contrast/mono/minimal) faisaient echouer
#   validate_export_job() a l'export, et les 2 themes export-only
#   (light-basic, light-alt) n'etaient jamais proposables depuis la TUI.
# Comment il sera utilise :
# - screens/settings_screen.py (liste des themes proposes),
#   widgets/theme_badge.py (libelle du theme actif) : available_theme_names().
# - screens/export_dialog.py (Select de theme d'export) :
#   available_export_theme_names().
#---------------------------------------------------------------------->
