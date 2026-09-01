# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Badge affichant le profil de rendu actif (complete/standard/reduced/mono)."""
from __future__ import annotations

from typing import Any

from omega_lib.terminal.models import RenderProfile
from textual.widgets import Static


class RenderProfileBadge(Static):
    """Etiquette texte simple, mise a jour par le render_profile_controller."""

    def __init__(self, profile: RenderProfile | None = None, **kwargs: Any) -> None:
        super().__init__(profile.value if profile else "", classes="omega-badge", **kwargs)

    def update_profile(self, profile: RenderProfile) -> None:
        self.update(profile.value)

# <-- INFO DEV ---------------------------------------------------------
# Role : rend visible a l'utilisateur quel profil de rendu a ete choisi
# (souvent automatiquement, d'apres terminal_detector.py) — important car
# ce choix peut degrader silencieusement les couleurs/ornements.
# Pourquoi dans interfaces/tui/widgets/ (charte) : affichage pur, la
# detection/decision vivent dans infrastructure/terminal/ et
# controllers/render_profile_controller.py.
# Ce qu'il ne contient PAS : aucune capacite de forcer un profil — ceci
# est une action utilisateur geree par settings_screen.py.
# Comment il sera utilise : screens/settings_screen.py, app.py (barre
# d'etat).
#---------------------------------------------------------------------->
