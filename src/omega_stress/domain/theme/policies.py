# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Catalogue des thèmes TUI et export, et règle de dégradation par profil de rendu.

Source d'autorité : Projet/themes.txt (valeurs extraites du code réel
d'omega-fire, catalogue partagé de la suite `omega-`, voir ARCHITECTURE.md
§8 et §0). Toute modification de palette doit d'abord être faite dans ce
document produit, jamais silencieusement ici.
"""
from __future__ import annotations

from dataclasses import dataclass

Color = str
"""Valeur de couleur opaque (hex `#rrggbb` ou nom Rich/Textual comme
"black"/"cyan") — interpretee par le consommateur (rendering/
textual_theme_builder.py ou infrastructure/exporters/html_theme_resolver.py),
jamais validee ici : ces valeurs sont figees par construction."""


@dataclass(frozen=True, slots=True)
class Palette:
    """Palette de couleurs d'un theme."""

    background: Color
    surface: Color
    panel: Color
    foreground: Color
    accent: Color
    secondary: Color
    success: Color
    warning: Color
    error: Color


@dataclass(frozen=True, slots=True)
class ThemeDefinition:
    """Un theme TUI complet : nom, palette, polarite sombre/claire."""

    name: str
    palette: Palette
    dark: bool


TUI_THEMES: dict[str, ThemeDefinition] = {
    "omega-base": ThemeDefinition(
        "omega-base",
        Palette("#0a0e1a", "#13182a", "#0f1320", "#e0e0e0", "#00d4ff", "#b4c2e0",
                "#b0f7b0", "#ffbc6e", "#ff5555"),
        dark=True,
    ),
    "omega-dark": ThemeDefinition(
        "omega-dark",
        Palette("#1e1e2e", "#252535", "#2a2a3e", "#d0d0e0", "#5b9bd5", "#6db3f2",
                "#7ec885", "#e5b95c", "#e06060"),
        dark=True,
    ),
    "omega-light": ThemeDefinition(
        "omega-light",
        Palette("#f8f9fa", "#ffffff", "#e9ecef", "#212529", "#0d6efd", "#6610f2",
                "#198754", "#ffc107", "#dc3545"),
        dark=False,
    ),
    "omega-neon": ThemeDefinition(
        "omega-neon",
        Palette("#0a0a12", "#12121e", "#0f0f1a", "#e0e0ff", "#ff00ff", "#00ffff",
                "#00ff9d", "#ffea00", "#ff0055"),
        dark=True,
    ),
    "omega-burn": ThemeDefinition(
        "omega-burn",
        Palette("#1a0505", "#2d0a0a", "#3d1010", "#f0e0d0", "#ff5500", "#ffaa00",
                "#ffaa00", "#ff7700", "#ff2200"),
        dark=True,
    ),
    "omega-pink": ThemeDefinition(
        "omega-pink",
        Palette("#1a1015", "#2a1a25", "#3a2a35", "#f0e0f0", "#ff80b0", "#b0b0ff",
                "#b0ffb0", "#ffd0a0", "#ff80a0"),
        dark=True,
    ),
    "omega-hack": ThemeDefinition(
        "omega-hack",
        Palette("#000000", "#001100", "#000a00", "#00ff00", "#00ff00", "#008800",
                "#00ff00", "#aaaa00", "#ff0000"),
        dark=True,
    ),
    "omega-contrast": ThemeDefinition(
        "omega-contrast",
        Palette("#1a1a2e", "#16213e", "#0f3460", "#f0f0f0", "#004ff9", "#ff6b35",
                "#06ffa5", "#ff9f1c", "#ff3535"),
        dark=True,
    ),
    "omega-mono": ThemeDefinition(
        "omega-mono",
        Palette("black", "black", "black", "white", "white", "ansi_bright_black",
                "green", "yellow", "red"),
        dark=True,
    ),
    "omega-minimal": ThemeDefinition(
        "omega-minimal",
        Palette("black", "black", "black", "white", "cyan", "white",
                "green", "yellow", "red"),
        dark=False,
    ),
}
"""Catalogue des 10 thèmes TUI. omega-mono et omega-minimal utilisent des
couleurs ANSI nommees plutot que du hex — voir Projet/themes.txt : c'est
leur nature meme (compatibilite TTY/SSH ancien), pas un manque."""

EXPORT_PALETTES: dict[str, Palette] = {
    "omega-base": Palette("#0a0e1a", "#0a0e1a", "#0a0e1a", "#e0e0e0", "#00d4ff",
                           "#b4c2e0", "#b0f7b0", "#ffbc6e", "#ff5555"),
    "omega-burn": Palette("#1a0505", "#1a0505", "#1a0505", "#f0e0d0", "#ff5500",
                           "#ffaa00", "#ffaa00", "#ff7700", "#ff2200"),
    "omega-neon": Palette("#0a0a12", "#0a0a12", "#0a0a12", "#e0e0ff", "#ff00ff",
                           "#00ffff", "#00ff9d", "#ffea00", "#ff0055"),
    "light-basic": Palette("#FFFFFF", "#FFFFFF", "#FFFFFF", "#1A1A1A", "#2563EB",
                            "#2563EB", "#16A34A", "#CA8A04", "#DC2626"),
    "light-alt": Palette("#FBF7EE", "#FBF7EE", "#FBF7EE", "#23301F", "#2F6B3A",
                          "#2F6B3A", "#3F8F4F", "#B4791F", "#B3402A"),
}
"""Catalogue des 5 thèmes d'export HTML, independant du theme TUI actif
(ARCHITECTURE.md §8). Seuls omega-base/omega-burn/omega-neon ont un
equivalent TUI ; light-basic et light-alt sont export-only (valeurs
propres, non sourcees d'omega-fire — voir Projet/themes.txt)."""

DEFAULT_TUI_THEME: str = "omega-base"
DEFAULT_EXPORT_THEME: str = "omega-base"


def _hex_to_rgb(value: Color) -> tuple[int, int, int] | None:
    if not value.startswith("#") or len(value) != 7:
        return None
    try:
        return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16))
    except ValueError:
        return None


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def degrade_to_grayscale(value: Color) -> Color:
    """Convertit une couleur hex en niveau de gris par luminance percue.
    Une valeur deja nommee (non hex, ex. omega-mono/omega-minimal) est
    retournee inchangee : elle est deja neutre par construction."""
    rgb = _hex_to_rgb(value)
    if rgb is None:
        return value
    gray = round(_relative_luminance(rgb))
    return f"#{gray:02x}{gray:02x}{gray:02x}"


def reduced_palette(palette: Palette) -> Palette:
    """Profil de rendu `reduced` : aplatit surface/panel sur background,
    conserve les autres couleurs telles quelles (ARCHITECTURE.md §8)."""
    return Palette(
        background=palette.background,
        surface=palette.background,
        panel=palette.background,
        foreground=palette.foreground,
        accent=palette.accent,
        secondary=palette.secondary,
        success=palette.success,
        warning=palette.warning,
        error=palette.error,
    )


def mono_palette(palette: Palette) -> Palette:
    """Profil de rendu `mono` : conversion en niveaux de gris par
    luminance percue — aucune palette dediee maintenue a la main par
    theme (ARCHITECTURE.md §8)."""
    return Palette(
        background=degrade_to_grayscale(palette.background),
        surface=degrade_to_grayscale(palette.background),
        panel=degrade_to_grayscale(palette.background),
        foreground=degrade_to_grayscale(palette.foreground),
        accent=degrade_to_grayscale(palette.accent),
        secondary=degrade_to_grayscale(palette.secondary),
        success=degrade_to_grayscale(palette.success),
        warning=degrade_to_grayscale(palette.warning),
        error=degrade_to_grayscale(palette.error),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Catalogue complet des 10 thèmes TUI et 5 thèmes d'export (donnees
#   pures), et regle generique de degradation reduced/mono.
# Pourquoi dans domain/theme/ (charte) :
# - Politique partagee de la suite `omega-` au sens de ARCHITECTURE.md §8 :
#   valeurs figees dans Projet/themes.txt, transcrites ici telles quelles.
# Ce qu'il ne contient PAS :
# - Aucune construction d'objet Textual/Rich (voir
#   interfaces/tui/rendering/textual_theme_builder.py, seul endroit ou
#   `textual` et ces donnees se combinent).
# - Aucune resolution de compatibilite terminal -> theme (les thèmes sont
#   tous manuellement selectionnables sur tout terminal ; c'est le profil
#   de rendu, decide independamment par domain/terminal/, qui degrade
#   n'importe quel theme — voir ARCHITECTURE.md §8, piege de nommage
#   omega-mono/mono).
# Points cles :
# - Palette est un type unique pour hex ET couleurs nommees (Color = str,
#   opaque) : omega-mono/omega-minimal utilisent des noms ANSI plutot que
#   du hex, degrade_to_grayscale() les laisse inchanges (deja neutres).
# - reduced_palette()/mono_palette() sont des fonctions PURES appliquees a
#   n'importe quel theme du catalogue, jamais une palette codee en dur par
#   theme x profil (evite 20 palettes a maintenir a la main).
# - EXPORT_PALETTES est un catalogue INDEPENDANT de TUI_THEMES (memes
#   trois noms omega-base/burn/neon, mais deux dict distincts) : pas de
#   correspondance automatique thème TUI -> thème export, voir plan produit
#   et ARCHITECTURE.md §8.
# Comment il sera utilise (apercu) :
# - domain/theme/service.py::resolve_palette() applique reduced_palette()/
#   mono_palette() selon le RenderProfile courant.
# - interfaces/tui/rendering/textual_theme_builder.py consomme TUI_THEMES.
# - infrastructure/exporters/html_theme_resolver.py consomme
#   EXPORT_PALETTES (lookup pur, aucun import Jinja2 a cet endroit).
#---------------------------------------------------------------------->
