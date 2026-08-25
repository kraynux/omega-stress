# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Badge affichant le nom du theme TUI actif."""
from __future__ import annotations

from typing import Any

from textual.widgets import Static


class ThemeBadge(Static):
    """Etiquette texte simple, mise a jour par le theme_controller."""

    def __init__(self, theme_name: str = "", **kwargs: Any) -> None:
        super().__init__(theme_name, classes="omega-badge", **kwargs)

    def update_theme(self, theme_name: str) -> None:
        self.update(theme_name)

# <-- INFO DEV ---------------------------------------------------------
# Role : reflete le nom du theme courant (parmi les 10 de
# domain/theme/policies.py::TUI_THEMES) quelque part dans l'UI.
# Pourquoi dans interfaces/tui/widgets/ (charte) : affichage pur, aucune
# logique de choix de theme (celle-ci vit dans
# controllers/theme_controller.py).
# Ce qu'il ne contient PAS : le changement de theme lui-meme — ce widget
# ne fait qu'afficher, jamais declencher app.theme = ... .
# Comment il sera utilise : screens/settings_screen.py, potentiellement
# une barre d'etat globale dans app.py.
#---------------------------------------------------------------------->
