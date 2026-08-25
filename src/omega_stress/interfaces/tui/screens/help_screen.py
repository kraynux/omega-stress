# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Aide : reference des raccourcis et des fonctions de l'application."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from omega_stress.core.enums import TestFamily
from omega_stress.interfaces.tui.presenters.load_reference_presenter import (
    load_reference_family_note,
)
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.widgets.load_reference_table import LoadReferenceTable

_SHORTCUTS = (
    ("Haut / Bas", "Naviguer entre les elements d'un ecran"),
    ("Tab / Maj+Tab", "Naviguer entre les champs d'un formulaire"),
    ("Echap", "Retour a l'ecran precedent (confirmation de sortie sur l'accueil)"),
    ("t", "Theme suivant"),
    ("a", "Cette aide"),
    ("q", "Quitter (avec confirmation)"),
)

_SECTIONS = (
    (
        "Test requetes / connexions / charge",
        "Trois familles de test encadrees : debit constant, nombre de "
        "connexions simultanees, ou montee progressive. Chaque lancement "
        "exige une cible (saisie manuelle ou cible epinglee) et une "
        "confirmation d'autorisation, sauf cible deja epinglee-autorisee.",
    ),
    (
        "Profils",
        "Un profil fige un jeu de parametres (cible, type de test, "
        "intensite, duree, seuils) pour le reutiliser tel quel — creer, "
        "puis figer, un profil depuis cet ecran.",
    ),
    (
        "Cibles",
        "Epingler une adresse dispense de recocher la confirmation "
        "d'autorisation a chaque lancement sur cette meme cible.",
    ),
    (
        "Historique",
        "Liste tous les runs passes : detail complet, ou relecture "
        "(uniquement pour un run lie a un profil fige).",
    ),
    (
        "Export",
        "Depuis le detail d'un run termine : JSON (donnees brutes, "
        "reimportables), CSV (analyse tabulaire), ou HTML (rapport "
        "lisible avec chronologie complete par intervalle).",
    ),
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche
    `a`, voir app.py::action_help()) ou depuis le bouton "Aide" de
    home.py."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("AIDE", classes="omega-title")
            yield Static("Raccourcis clavier", classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(f"{key:<14} {description}")
            yield Static("")
            yield Static("Fonctions", classes="omega-subtitle")
            for title, description in _SECTIONS:
                yield Static(f"[b]{title}[/b]\n{description}\n")
            yield Static("Reperes de charge (valeurs exactes par niveau)", classes="omega-subtitle")
            yield Static(
                f"[b]Test requetes[/b] — {load_reference_family_note(TestFamily.REQUEST)}\n"
                f"[b]Test connexions[/b] — {load_reference_family_note(TestFamily.CONNECTION)}\n"
                f"[b]Test charge[/b] — {load_reference_family_note(TestFamily.RAMP)}\n"
            )
            yield LoadReferenceTable(id="load-reference")
            yield Static("")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Reference statique des raccourcis clavier et des fonctions de
#   l'application, accessible depuis n'importe quel ecran.
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Ecran de presentation pur, contenu fixe — aucun appel a application/.
# Ce qu'il ne contient PAS :
# - Aucun couplage a interfaces/cli/ (ARCHITECTURE.md §0 : les deux
#   adaptateurs de presentation restent independants, meme si le CLI
#   pourrait fournir un texte d'aide equivalent via argparse) : le
#   contenu est duplique ici volontairement plutot que d'importer
#   interfaces/cli/main.py::build_parser(), qui violerait de toute facon
#   le contrat import-linter "textual seulement dans interfaces.tui" des
#   que ce module serait importe transitivement par un module CLI.
# Points cles :
# - _SHORTCUTS/_SECTIONS sont des tuples module-level plutot que des
#   chaines codees en dur dans compose() : plus facile a maintenir a jour
#   quand un raccourci ou une fonction change ailleurs dans le projet.
# - Bouton "Retour" (2026-08-24) : avant ce correctif, cet ecran etait le
#   SEUL de toute l'application sans bouton "Retour" explicite (Escape
#   suffisait deja via OmegaScreen.action_back(), _base.py, mais aucun
#   moyen 100% souris de le quitter) — incoherent avec tous les autres
#   ecrans, qui offrent tous ce bouton. dismiss() sans argument, meme
#   comportement qu'Escape (OmegaScreen[None]).
# Comment il sera utilise :
# - interfaces/tui/app.py::action_help() (touche `a`, global).
# - interfaces/tui/screens/home.py (bouton "Aide").
#---------------------------------------------------------------------->
