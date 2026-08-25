# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Traduit le profil de rendu deja decide en choix concret de feuille de style."""
from __future__ import annotations

from pathlib import Path

from omega_stress.core.enums import RenderProfile

_STYLES_DIR = Path(__file__).parent.parent / "styles"

_PROFILE_STYLESHEETS: dict[RenderProfile, str] = {
    RenderProfile.COMPLETE: "complete.tcss",
    RenderProfile.STANDARD: "standard.tcss",
    RenderProfile.REDUCED: "reduced.tcss",
    RenderProfile.MONO: "mono.tcss",
}


def stylesheet_paths_for(profile: RenderProfile) -> tuple[Path, Path]:
    """Retourne (base.tcss, <profil>.tcss) — base est toujours chargee en
    premier (regles communes), le fichier du profil vient ensuite
    affiner/surcharger (ARCHITECTURE.md §2.4)."""
    return (_STYLES_DIR / "base.tcss", _STYLES_DIR / _PROFILE_STYLESHEETS[profile])


def use_simplified_widgets(profile: RenderProfile) -> bool:
    """True si les variantes simplifiees de widgets (tables sans bordures
    riches, pas d'ornements non-ASCII) doivent etre utilisees — reduced
    et mono uniquement."""
    return profile in (RenderProfile.REDUCED, RenderProfile.MONO)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit un RenderProfile (deja decide par
#   domain/terminal/service.py::resolve_render_profile, jamais recalcule
#   ici) en chemins de feuilles de style et en choix de variantes de
#   widgets.
# Pourquoi dans interfaces/tui/rendering/ (charte) :
# - Applique une decision deja prise par le domaine, ne la recalcule
#   jamais (ARCHITECTURE.md §2.4, anti-pattern explicitement interdit en
#   §10 : "Faire decider render_profile_resolver.py du profil applicable
#   au lieu de simplement appliquer la decision deja prise").
# Ce qu'il ne contient PAS :
# - Aucune lecture de terminal, aucun appel a
#   infrastructure/terminal/detector.py.
# - Aucune construction de theme de couleur (voir
#   textual_theme_builder.py, notion independante — ARCHITECTURE.md §8).
# Points cles :
# - stylesheet_paths_for() retourne TOUJOURS 2 chemins (base + profil) :
#   base.tcss porte les regles structurelles communes aux 4 profils,
#   jamais dupliquees.
# - use_simplified_widgets() est le seul point de decision consulte par
#   les widgets eux-memes (ex. history_table.py) pour savoir s'ils
#   doivent afficher une variante allegee.
# Comment il sera utilise (apercu) :
# - interfaces/tui/rendering/stylesheet_loader.py consomme
#   stylesheet_paths_for().
# - interfaces/tui/controllers/render_profile_controller.py et les widgets
#   consomment use_simplified_widgets().
#---------------------------------------------------------------------->
