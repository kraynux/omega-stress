# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Construction des objets textual.theme.Theme a partir de domain/theme/policies.py.

Seul fichier, avec le reste de interfaces/tui/, autorise a combiner donnees
de theme et API Textual (ARCHITECTURE.md §2.4, §8).
"""
from __future__ import annotations

from omega_lib.theme.policies import TUI_THEMES, Palette, ThemeDefinition
from textual.theme import Theme as TextualTheme


def build_textual_theme(definition: ThemeDefinition) -> TextualTheme:
    """Traduit une palette de domain/theme/policies.py en objet
    textual.theme.Theme. Textual distingue `primary` (couleur principale,
    obligatoire) et `accent` (couleur d'appoint optionnelle) ; notre
    modele de domaine n'a que `accent` (couleur principale) et
    `secondary` — mappe donc `primary <- palette.accent` et laisse
    `accent` non renseigne (Textual derive les teintes manquantes des
    couleurs fournies plutot que d'inventer une troisieme teinte non
    presente dans le catalogue)."""
    palette = definition.palette
    return TextualTheme(
        name=definition.name,
        primary=palette.accent,
        secondary=palette.secondary,
        warning=palette.warning,
        error=palette.error,
        success=palette.success,
        foreground=palette.foreground,
        background=palette.background,
        surface=palette.surface,
        panel=palette.panel,
        dark=definition.dark,
        variables={},
    )


def build_all_textual_themes() -> tuple[TextualTheme, ...]:
    """Construit les 10 themes du catalogue, dans l'ordre de
    domain/theme/policies.py::TUI_THEMES."""
    return tuple(build_textual_theme(definition) for definition in TUI_THEMES.values())


def build_textual_theme_from_palette(name: str, palette: Palette, *, dark: bool) -> TextualTheme:
    """Variante pour une palette DEGRADEE (reduced/mono), produite a la
    volee par domain/theme/service.py::resolve_palette() plutot que
    directement issue du catalogue statique."""
    return TextualTheme(
        name=name,
        primary=palette.accent,
        secondary=palette.secondary,
        warning=palette.warning,
        error=palette.error,
        success=palette.success,
        foreground=palette.foreground,
        background=palette.background,
        surface=palette.surface,
        panel=palette.panel,
        dark=dark,
        variables={},
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit le catalogue de themes TUI (domain/theme/policies.py) et les
#   palettes degradees (domain/theme/service.py) en objets
#   textual.theme.Theme consommables par l'App Textual.
# Pourquoi dans interfaces/tui/rendering/ (charte) :
# - Seul endroit du projet ou `textual.theme.Theme` est construit — la
#   construction d'un objet Theme Textual est un acte de presentation,
#   jamais un detail d'infrastructure (ARCHITECTURE.md §2.4).
# Ce qu'il ne contient PAS :
# - Aucune donnee de palette en dur (tout vient de domain/theme/policies.py).
# - Aucune decision de quel theme appliquer (c'est
#   application/commands/select_theme.py, deja construit).
# Points cles :
# - Le mapping primary<-accent est une interpretation documentee ci-dessus
#   (Textual a un systeme a deux couleurs primary/accent, notre domaine
#   n'en a qu'une — accent — plus une secondary).
# - build_textual_theme_from_palette() est necessaire car
#   domain/theme/service.py::resolve_palette() peut produire une Palette
#   degradee qui n'existe dans aucune entree de TUI_THEMES (ex. version
#   grayscale d'omega-neon) : ce cas ne peut pas passer par
#   build_textual_theme(), qui exige un ThemeDefinition complet.
# Comment il sera utilise (apercu) :
# - interfaces/tui/app.py enregistre les themes au demarrage
#   (self.register_theme() pour chacun) et bascule via self.theme = nom.
# - build_textual_theme_from_palette() n'est pas encore appelee en V1 : la
#   degradation reduced/mono a chaud (re-teinte, pas seulement structure)
#   reste un axe d'amelioration differe, voir interfaces/tui/app.py, INFO
#   DEV, "Ce qu'il ne contient PAS" — seule la degradation STRUCTURELLE
#   (styles/{reduced,mono}.tcss) est cablee pour l'instant. La fonction
#   reste ecrite et testee (prete a etre branchee) pour ne pas bloquer ce
#   futur cablage.
#---------------------------------------------------------------------->
