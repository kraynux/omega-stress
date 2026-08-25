# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Decision de repli et de degradation d'un theme (theme_compatibility_service, §8)."""
from __future__ import annotations

from omega_stress.core.enums import RenderProfile
from omega_stress.domain.theme.models import AppliedTheme
from omega_stress.domain.theme.policies import (
    DEFAULT_TUI_THEME,
    TUI_THEMES,
    Palette,
    mono_palette,
    reduced_palette,
)


def resolve_applied_theme(requested_theme: str, *, render_profile: RenderProfile) -> AppliedTheme:
    """Resout le theme effectivement applique : repli vers le theme par
    defaut si le nom demande est inconnu du catalogue. Ne juge jamais de
    la compatibilite couleur du terminal — c'est deja couvert en amont par
    domain/terminal/service.py, qui decide render_profile independamment
    du choix de theme (ARCHITECTURE.md §8)."""
    fell_back_from: str | None = None
    theme_name = requested_theme
    if theme_name not in TUI_THEMES:
        fell_back_from = requested_theme
        theme_name = DEFAULT_TUI_THEME

    return AppliedTheme(
        theme_name=theme_name, render_profile=render_profile, fell_back_from=fell_back_from
    )


def resolve_palette(theme_name: str, render_profile: RenderProfile) -> Palette:
    """Retourne la palette a utiliser pour un theme et un profil de rendu
    donnes, en appliquant la degradation generique si necessaire."""
    definition = TUI_THEMES.get(theme_name, TUI_THEMES[DEFAULT_TUI_THEME])
    if render_profile is RenderProfile.MONO:
        return mono_palette(definition.palette)
    if render_profile is RenderProfile.REDUCED:
        return reduced_palette(definition.palette)
    return definition.palette

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - resolve_applied_theme() : decide quel theme est reellement actif
#   (repli si nom inconnu).
# - resolve_palette() : produit la palette concrete a utiliser, degradee
#   selon le profil de rendu courant.
# Pourquoi dans domain/theme/ (charte) :
# - "theme_compatibility_service" au sens de ARCHITECTURE.md §2 : combine
#   des politiques pures (domain/theme/policies.py) sans I/O ni dependance
#   a Textual.
# Ce qu'il ne contient PAS :
# - Aucune construction d'objet textual.theme.Theme (voir
#   interfaces/tui/rendering/textual_theme_builder.py, seul endroit
#   autorise a combiner ces donnees et l'API Textual).
# - Aucune persistance du theme choisi (c'est
#   infrastructure/settings/json_settings_store.py via le port
#   settings_store).
# - Aucune decision de profil de rendu (c'est domain/terminal/service.py —
#   ce fichier consomme render_profile en parametre, il ne le calcule
#   jamais).
# Points cles :
# - resolve_palette() ne verifie jamais la compatibilite terminal du theme
#   demande (ex. omega-neon sur un terminal 16 couleurs) : dans le modele
#   omega-stress, N'IMPORTE QUEL theme reste selectionnable manuellement
#   sur n'importe quel terminal — c'est le profil de rendu qui degrade
#   uniformement, pas un mecanisme de compatibilite par theme (a la
#   difference du modele `is_compatible()` par theme d'omega-fire, voir
#   ARCHITECTURE.md §8 et Projet/themes.txt).
# Comment il sera utilise (apercu) :
# - application/commands/select_theme.py appelle resolve_applied_theme().
# - interfaces/tui/rendering/textual_theme_builder.py appelle
#   resolve_palette() pour obtenir les couleurs a injecter dans le Theme
#   Textual courant.
# - infrastructure/exporters/html_theme_resolver.py n'utilise PAS ce
#   service : il consomme directement
#   domain/theme/policies.py::EXPORT_PALETTES (catalogue independant, pas
#   de profil de rendu pour un export HTML statique).
#---------------------------------------------------------------------->
