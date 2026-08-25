# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entite representant l'etat d'un theme applique."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import RenderProfile


@dataclass(frozen=True, slots=True)
class AppliedTheme:
    """Theme effectivement applique a l'interface : nom retenu, profil de
    rendu courant, et repli eventuel si le theme demande etait inconnu."""

    theme_name: str
    render_profile: RenderProfile
    fell_back_from: str | None = None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Represente le resultat d'une decision de theme : quel theme est
#   effectivement actif, sous quel profil de rendu, et s'il y a eu repli.
# Pourquoi dans domain/theme/ (charte) :
# - Value object metier pur, produit par domain/theme/service.py.
# Ce qu'il ne contient PAS :
# - Aucune palette resolue (voir domain/theme/service.py::resolve_palette,
#   qui retourne un Palette separement — AppliedTheme ne fait qu'identifier
#   QUEL theme et QUEL profil, pas la palette concrete qui en decoule).
# - Aucune construction d'objet Textual (voir
#   interfaces/tui/rendering/textual_theme_builder.py).
# Points cles :
# - fell_back_from est None dans le cas normal (theme demande = theme
#   applique) ; renseigne uniquement si le nom demande etait inconnu du
#   catalogue (domain/theme/policies.py::TUI_THEMES).
# Comment il sera utilise (apercu) :
# - application/commands/select_theme.py produit un AppliedTheme.
# - interfaces/tui/presenters/theme_presenter.py et
#   interfaces/tui/widgets/theme_badge.py l'affichent, y compris
#   l'avertissement de repli le cas echeant.
#---------------------------------------------------------------------->
