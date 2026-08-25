# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : choisir un theme TUI et le persister."""
from __future__ import annotations

from omega_stress.application.dto.mappers import applied_theme_to_dto
from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.core.enums import RenderProfile
from omega_stress.domain.theme.service import resolve_applied_theme
from omega_stress.ports.settings_store import SettingsStore

_SETTINGS_KEY = "theme"


def select_theme(
    theme_name: str, *, render_profile: RenderProfile, settings_store: SettingsStore
) -> ThemeStatusDTO:
    """Resout le theme demande (repli si nom inconnu) et persiste le choix
    effectivement retenu — jamais le nom demande brut si un repli a eu
    lieu, pour que la prochaine ouverture reparte d'un etat coherent."""
    applied = resolve_applied_theme(theme_name, render_profile=render_profile)
    settings_store.set(_SETTINGS_KEY, applied.theme_name)
    return applied_theme_to_dto(applied)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Applique et persiste un choix de theme utilisateur (touche `t`, ecran
#   Reglages).
# Pourquoi dans application/commands/ (charte) :
# - Orchestre domain/theme/service.py::resolve_applied_theme() et le port
#   settings_store, sans decider lui-meme de la logique de repli.
# Ce qu'il ne contient PAS :
# - Aucune palette, aucune construction d'objet Textual (voir
#   interfaces/tui/rendering/textual_theme_builder.py, qui lira le theme
#   persiste ici au prochain demarrage via
#   application/services/theme_selection_service.py — a construire).
# - Aucune decision de profil de rendu : render_profile est recu en
#   parametre, deja decide par domain/terminal/service.py en amont.
# Points cles :
# - _SETTINGS_KEY = "theme" est la SEULE definition de ce nom de cle dans
#   tout le projet : tout autre code lisant la preference de theme doit
#   passer par ce module (ou un futur
#   application/services/theme_selection_service.py qui la reutiliserait),
#   jamais reecrire la chaine "theme" ailleurs.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/theme_controller.py (touche `t`),
#   interfaces/tui/screens/settings_screen.py.
#---------------------------------------------------------------------->
