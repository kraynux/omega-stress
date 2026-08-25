# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : applique, persiste et fait defiler le theme TUI actif."""
from __future__ import annotations

from omega_stress.application.commands.select_theme import select_theme
from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.core.enums import RenderProfile
from omega_stress.interfaces.tui.presenters.theme_presenter import available_theme_names
from omega_stress.ports.settings_store import SettingsStore


def choose_theme(
    theme_name: str, *, render_profile: RenderProfile, settings_store: SettingsStore
) -> ThemeStatusDTO:
    """Applique et persiste le theme choisi explicitement (ecran Reglages)."""
    return select_theme(theme_name, render_profile=render_profile, settings_store=settings_store)


def cycle_theme(
    current_theme_name: str,
    *,
    direction: int,
    render_profile: RenderProfile,
    settings_store: SettingsStore,
) -> ThemeStatusDTO:
    """Passe au theme suivant (direction=1) ou precedent (direction=-1)
    du catalogue, avec bouclage (voir plan produit, touche `t`)."""
    names = available_theme_names()
    index = names.index(current_theme_name) if current_theme_name in names else 0
    next_index = (index + direction) % len(names)
    return choose_theme(
        names[next_index], render_profile=render_profile, settings_store=settings_store
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de screens/settings_screen.py (et de la touche
#   `t` globale de app.py) vers application/commands/select_theme.py.
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - cycle_theme() est un besoin de PRESENTATION (navigation clavier dans
#   un catalogue) sans equivalent dans application/ : select_theme() ne
#   connait qu'un nom de theme cible, jamais la notion de "suivant".
# Ce qu'il ne contient PAS :
# - Aucune palette ni construction de Theme Textual (voir
#   rendering/textual_theme_builder.py, qui lira le theme applique ici au
#   prochain rendu).
# Points cles :
# - cycle_theme() retombe sur l'index 0 si current_theme_name est inconnu
#   (ex. premier lancement) plutot que de lever une exception : coherent
#   avec le principe de repli deja pose par
#   domain/theme/service.py::resolve_applied_theme().
# Comment il sera utilise :
# - screens/settings_screen.py, app.py (raccourci clavier `t`).
#---------------------------------------------------------------------->
