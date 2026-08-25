# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de confirmation generique avant une action destructrice."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static


class ConfirmScreen(Screen[bool]):
    """Demande confirmation avant une action irreversible (titre/message
    parametrables) — pousse par screens/settings_screen.py pour les
    purges de cibles/historique. Resultat bool transmis au callback de
    push_screen()."""

    def __init__(self, *, title: str, message: str) -> None:
        super().__init__()
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        with Middle(), Center(), Vertical(classes="omega-confirm-box"):
            yield Static(self._title, classes="omega-confirm-title")
            yield Static(self._message, classes="omega-confirm-message")
            with Horizontal(classes="omega-confirm-buttons"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Oui, confirmer", id="confirm", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Non, annuler", id="cancel", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'arret generique avant une action destructrice (purge de
#   cibles ou d'historique, voir screens/settings_screen.py) — evite
#   qu'un clic accidentel efface des donnees sans avertissement.
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Ecran de presentation pur, Screen[bool] (pas Screen[None] comme
#   OmegaScreen, voir _base.py) : sa seule raison d'etre est de retourner
#   une decision binaire a l'appelant via push_screen(screen, callback),
#   jamais de dismiss() sans argument.
# Ce qu'il ne contient PAS :
# - Aucune execution de l'action confirmee : ce fichier ne fait que
#   retourner True/False, l'appelant decide ensuite d'appeler ou non le
#   controller correspondant.
# - N'herite pas de OmegaScreen (_base.py) : meme raison que
#   quit_confirm.py, `echap` doit annuler (revenir sans agir), pas
#   remonter au sens de "Retour" ailleurs.
# Ce qu'il contient a la place de screens/quit_confirm.py :
# - Le plan initial envisageait de generaliser quit_confirm.py en lui
#   ajoutant title/message et de le reutiliser pour ces deux besoins.
# - Deviation assumee (2026-08-24) : quit_confirm.py reste un ecran
#   distinct, non touche. Le generaliser aurait exige de re-verifier deux
#   chemins d'appel deja testes et stables (app.py::action_quit(),
#   home.py::action_back()) pour un gain purement interne (pas de
#   difference visible pour l'utilisateur, qui obtient la meme
#   confirmation dans les deux cas) — risque de regression sans benefice
#   utilisateur correspondant. ConfirmScreen sert desormais les DEUX
#   nouveaux besoins (purge de cibles, purge d'historique) sans toucher
#   au chemin de sortie existant.
# Points cles :
# - variant="error" sur "Oui, confirmer" : meme signal visuel que
#   quit_confirm.py pour une action destructrice.
# - .omega-confirm-box (2026-08-24, styles/base.tcss) : un seul cadre
#   borde (facon console) englobant titre+message+boutons, tous a la MEME
#   largeur fixe — corrige un defaut visuel reel rapporte ("tout centré
#   en mode console (BOX)") : le titre (ex-classe "omega-title", bordee
#   independamment, width:auto) semblait centre car sa propre boite etait
#   etroite, mais le message (ex-classe "omega-subtitle", sans largeur
#   propre) s'etalait sur toute la largeur disponible et restait
#   visuellement plaque a gauche a l'interieur d'un Center() qui ne
#   centre que la BOITE d'un widget, jamais son texte a l'interieur d'une
#   boite deja pleine largeur — meme correctif applique a
#   quit_confirm.py.
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/settings_screen.py (purge des cibles
#   recentes/toutes, purge de l'historique des runs).
#---------------------------------------------------------------------->
