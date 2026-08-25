# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de confirmation avant fermeture de l'application."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static


class QuitConfirmScreen(Screen[bool]):
    """Demande confirmation avant de fermer l'application — pousse par
    app.py::action_quit() (touche `q`) et par home.py::action_back()
    (touche `echap` depuis l'accueil, qui n'a pas d'autre "retour"
    possible). Resultat bool transmis au callback de push_screen()."""

    def compose(self) -> ComposeResult:
        with Middle(), Center(), Vertical(classes="omega-confirm-box"):
            yield Static("QUITTER OMEGA-STRESS ?", classes="omega-confirm-title")
            yield Static(
                "Tout test en cours sera interrompu.", classes="omega-confirm-message"
            )
            with Horizontal(classes="omega-confirm-buttons"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Oui, quitter", id="confirm", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Non, continuer", id="cancel", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'arret unique avant toute fermeture de l'application, qu'elle
#   soit demandee par la touche `q` (app.py) ou par `echap` depuis
#   l'ecran d'accueil (home.py) — evite qu'une pression accidentelle
#   ferme l'application sans avertissement, en particulier pendant qu'un
#   test tourne (voir widgets/run_progress.py, phase suivante).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Ecran de presentation pur, Screen[bool] (pas Screen[None] comme
#   OmegaScreen, voir _base.py) : sa seule raison d'etre est de retourner
#   une decision binaire a l'appelant via push_screen(screen, callback),
#   jamais de dismiss() sans argument.
# Ce qu'il ne contient PAS :
# - Aucune interruption effective d'un run en cours : le message avertit
#   seulement, la fermeture reelle (App.exit()) reste decidee par
#   l'appelant apres reception du resultat True.
# - N'herite pas de OmegaScreen (_base.py) : `echap` sur CET ecran
#   precis doit annuler la sortie (revenir sans quitter), pas remonter
#   au meme sens que "Retour" ailleurs — comportement identique au
#   bouton "Non, continuer" via le binding par defaut de Textual
#   (Screen.dismiss() sans argument sur `escape`, ce qui reviendrait a
#   dismiss(None) et casserait le typage Screen[bool] ; laisse donc
#   volontairement sans binding clavier dedie, seuls les boutons
#   decident).
# Points cles :
# - variant="error" sur "Oui, quitter" : seul bouton de toute
#   l'application a utiliser cette variante Textual (rouge), signal
#   visuel coherent avec la gravite de l'action.
# - .omega-confirm-box (2026-08-24, styles/base.tcss, meme classe que
#   screens/confirm.py — voir son INFO DEV pour le bug complet) : cadre
#   borde unique englobant titre+message+boutons a la meme largeur fixe,
#   remplace "omega-title"/"omega-subtitle" (bordage/largeur
#   incoherents entre les deux, le message paraissait plaque a gauche
#   plutot que centre comme le titre).
# Comment il sera utilise (apercu) :
# - interfaces/tui/app.py::action_quit() (surcharge de App.action_quit).
# - interfaces/tui/screens/home.py::action_back().
#---------------------------------------------------------------------->
