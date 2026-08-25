# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Politiques de terminal : matrice famille -> profil de rendu, paliers de taille.

Source produit : plan_omega-stress_v5.md, sections "Matrice terminal par
defaut" et "Taille minimale". Politique de demarrage, pas une verite
absolue (config, police, tmux/SSH font varier les capacites reelles) — voir
domain/terminal/service.py pour la combinaison finale.
"""
from __future__ import annotations

from omega_stress.core.enums import RenderProfile

TERMINAL_FAMILY_PROFILES: dict[str, RenderProfile] = {
    "ghostty": RenderProfile.COMPLETE,
    "alacritty": RenderProfile.COMPLETE,
    "wezterm": RenderProfile.COMPLETE,
    "kitty": RenderProfile.COMPLETE,
    "konsole": RenderProfile.STANDARD,
    "gnome-terminal": RenderProfile.STANDARD,
    "terminator": RenderProfile.STANDARD,
    "xfce4-terminal": RenderProfile.STANDARD,
    "urxvt": RenderProfile.REDUCED,
    "xterm": RenderProfile.REDUCED,
    "linux-tty": RenderProfile.MONO,
    "ssh-modern": RenderProfile.REDUCED,
    "ssh-legacy": RenderProfile.MONO,
}
"""Profil initial par famille de terminal detectee (noms normalises en
minuscules avec tirets, voir infrastructure/terminal/detector.py)."""

DEFAULT_RENDER_PROFILE: RenderProfile = RenderProfile.REDUCED
"""Profil applique quand la famille de terminal n'est pas reconnue :
prudent par defaut, ni le plus riche ni le plus degrade."""

_SIZE_THRESHOLDS: tuple[tuple[int, int, RenderProfile], ...] = (
    (120, 32, RenderProfile.COMPLETE),
    (100, 28, RenderProfile.STANDARD),
    (80, 24, RenderProfile.REDUCED),
)
"""Paliers (colonnes minimales, lignes minimales, plafond de profil), du
plus exigeant au moins exigeant. En dessous du dernier palier : MONO (ou
ecran d'avertissement, decide par la presentation, pas ici)."""

MINIMUM_USABLE_COLUMNS: int = 80
MINIMUM_USABLE_ROWS: int = 24

_PROFILE_ORDER: tuple[RenderProfile, ...] = (
    RenderProfile.MONO,
    RenderProfile.REDUCED,
    RenderProfile.STANDARD,
    RenderProfile.COMPLETE,
)
"""Ordre du moins au plus riche, utilise par most_restrictive()."""


def render_profile_ceiling_for_size(columns: int, rows: int) -> RenderProfile:
    """Plafond de profil de rendu autorise pour une taille de terminal
    donnee, independamment de la famille de terminal detectee."""
    for min_columns, min_rows, profile in _SIZE_THRESHOLDS:
        if columns >= min_columns and rows >= min_rows:
            return profile
    return RenderProfile.MONO


def most_restrictive(a: RenderProfile, b: RenderProfile) -> RenderProfile:
    """Retourne le profil le moins riche des deux (jamais plus riche que
    l'un ou l'autre plafond)."""
    return a if _PROFILE_ORDER.index(a) <= _PROFILE_ORDER.index(b) else b

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte la matrice famille de terminal -> profil de rendu initial, les
#   paliers de taille minimale, et l'ordre de restriction entre profils.
# Pourquoi dans domain/terminal/ (charte) :
# - Politique de produit au sens de ARCHITECTURE.md §2 : ces valeurs
#   figurent telles quelles dans des tableaux du plan produit.
#   infrastructure/terminal/raw_capabilities.py ne fait que remonter des
#   signaux bruts, jamais ces tables.
# Ce qu'il ne contient PAS :
# - Aucune decision finale (c'est domain/terminal/service.py qui combine
#   family_profile et size_ceiling).
# - Aucune lecture de variable d'environnement ni de taille reelle du
#   terminal (infrastructure/terminal/raw_capabilities.py).
# - Aucun theme de couleur (domain/theme/policies.py, notion independante,
#   voir ARCHITECTURE.md §8).
# Points cles :
# - render_profile_ceiling_for_size() retourne un PLAFOND, pas le profil
#   final : une petite taille peut degrader un terminal par ailleurs
#   COMPLETE, jamais l'inverse (voir most_restrictive()).
# - most_restrictive() est une fonction pure sur l'enum RenderProfile,
#   reutilisable independamment des sources family/size.
# Comment il sera utilise (apercu) :
# - domain/terminal/service.py::resolve_render_profile() combine
#   TERMINAL_FAMILY_PROFILES et render_profile_ceiling_for_size() via
#   most_restrictive().
#---------------------------------------------------------------------->
