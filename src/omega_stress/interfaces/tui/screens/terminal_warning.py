# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran d'avertissement : terminal trop petit ou profil de rendu degrade."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, Middle
from textual.screen import Screen
from textual.widgets import Button, Static


class TerminalWarningScreen(Screen[None]):
    """Affiche avant home.py quand le profil de rendu resolu par
    controllers/startup_controller.py est `mono`, ou que la taille du
    terminal est sous le seuil minimal (domain/terminal/policies.py::
    MINIMUM_USABLE_COLUMNS/ROWS) — jamais un blocage, seulement un avis."""

    def __init__(self, *, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Middle(), Center():
            yield Static("TERMINAL LIMITE", classes="omega-title")
            yield Static(self._message, classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Continuer quand meme", id="continue", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "continue":
            self.dismiss()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Informe l'utilisateur que le rendu sera degrade (ou tres restreint),
#   sans jamais empecher l'usage de l'application (ARCHITECTURE.md §8 :
#   n'importe quel theme/profil reste utilisable sur n'importe quel
#   terminal).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Affichage pur, ne recalcule jamais le profil de rendu (deja decide en
#   amont par domain/terminal/service.py, relaye par
#   controllers/render_profile_controller.py).
# Ce qu'il ne contient PAS :
# - Aucune option de forcer un profil different depuis cet ecran (deja le
#   role de screens/settings_screen.py) : ce message est informatif, pas
#   un point de configuration.
# Points cles :
# - message est fourni par l'appelant (app.py), deja compose a partir du
#   TerminalStatusDTO courant : cet ecran ne connait aucun detail de
#   colonnes/lignes lui-meme.
# Comment il sera utilise :
# - interfaces/tui/app.py, au demarrage (2026-08-24 : plus d'ecran splash
#   avant, retire), si le profil resolu est mono ou la taille sous le
#   seuil minimal.
#---------------------------------------------------------------------->
