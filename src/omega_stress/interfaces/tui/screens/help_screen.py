# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Aide : reference des raccourcis et des fonctions de l'application."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from omega_stress.core.enums import TestFamily
from omega_stress.domain.load.policies import SAFETY_MODE_DESCRIPTION
from omega_stress.interfaces.tui.presenters.load_reference_presenter import (
    load_reference_family_note,
)
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.widgets.duration_preset_table import DurationPresetTable
from omega_stress.interfaces.tui.widgets.load_reference_table import LoadReferenceTable
from omega_stress.shared.i18n import _

_SHORTCUTS = (
    (_("Haut / Bas"), _("Naviguer entre les éléments d'un écran")),
    (_("Tab / Maj+Tab"), _("Naviguer entre les champs d'un formulaire")),
    (_("Échap"), _("Retour à l'écran précédent (confirmation de sortie sur l'accueil)")),
    ("t", _("Thème suivant")),
    ("a", _("Cette aide")),
    ("q", _("Quitter (avec confirmation)")),
)

_SECTIONS = (
    (
        _("Test requêtes / connexions / charge"),
        _("Trois familles de test encadrées : débit constant, nombre de connexions "
          "simultanées, ou montée progressive. Chaque lancement exige une cible (saisie "
          "manuelle ou cible épinglée) et une confirmation d'autorisation, sauf cible déjà "
          "épinglée-autorisée."),
    ),
    (
        _("Profils"),
        _("Un profil fige un jeu de paramètres (cible, type de test, intensité, durée, seuils) "
          "pour le réutiliser tel quel — créer, puis figer, un profil depuis cet écran."),
    ),
    (
        _("Cibles"),
        _("Épingler une adresse dispense de recocher la confirmation d'autorisation à chaque "
          "lancement sur cette même cible."),
    ),
    (
        _("Historique"),
        _("Liste tous les runs passés : détail complet, ou relecture (uniquement pour un run "
          "lié à un profil figé)."),
    ),
    (
        _("Export"),
        _("Depuis le détail d'un run terminé : JSON (données brutes, réimportables), CSV "
          "(analyse tabulaire), ou HTML (rapport lisible avec chronologie complète par "
          "intervalle)."),
    ),
    (
        _("Profils de durée D1-D6 (mode profil)"),
        _("En plus de la durée manuelle (1 à 5 min selon le niveau), chaque écran de lancement "
          "propose un mode profil : une durée fixe nommée (1 à 120 min) qui limite les niveaux "
          "accessibles, avec un niveau supplémentaire débloqué par une confirmation renforcée "
          "(texte exact à saisir). Voir le tableau ci-dessous."),
    ),
    (
        _("Calibrage"),
        _("Mesure la capacité réelle de CETTE machine (pas la cible testée) via un serveur de "
          "boucle locale, par paliers de charge croissante. Le résultat (VU_safe/RPS_safe) "
          "n'est pas appliqué automatiquement aux tests réels : consultable depuis l'écran "
          "Calibrage, et utile comme repère quand le mode sécurité est désactivé (voir "
          "ci-dessous)."),
    ),
    (
        _("Mode sécurité"),
        SAFETY_MODE_DESCRIPTION
        + _(" Si un calibrage a été effectué sur cette machine, l'écran de lancement compare "
            "le niveau choisi à son enveloppe dès que la case est décochée."),
    ),
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche
    `a`, voir app.py::action_help()) ou depuis le bouton "Aide" de
    home.py."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("AIDE"), classes="omega-title")
            yield Static(_("Raccourcis clavier"), classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(_("{key:<14} {description}").format(key=key, description=description))
            yield Static("")
            yield Static(_("Fonctions"), classes="omega-subtitle")
            for title, description in _SECTIONS:
                yield Static(f"[b]{title}[/b]\n{description}\n")
            yield Static(
                _("Repères de charge (valeurs exactes par niveau)"), classes="omega-subtitle"
            )
            yield Static(
                _(
                    "[b]Test requêtes[/b] — {value}\n[b]Test connexions[/b] — {value2}\n[b]Test "
                    "charge[/b] — {value3}\n"
                ).format(
                    value=load_reference_family_note(TestFamily.REQUEST),
                    value2=load_reference_family_note(TestFamily.CONNECTION),
                    value3=load_reference_family_note(TestFamily.RAMP),
                )
            )
            yield LoadReferenceTable(id="load-reference")
            yield Static("")
            yield Static(_("Profils de durée D1-D6 (mode profil)"), classes="omega-subtitle")
            yield DurationPresetTable(id="duration-preset-reference")
            yield Static("")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
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
# - DurationPresetTable (2026-09-01) : AVANT ce correctif, le mode
#   "profil" D1-D6 (deja fonctionnel dans les 3 ecrans de lancement et le
#   CLI) n'apparaissait nulle part ici — bug de decouvrabilite reel
#   signale par l'utilisateur en test ("je vois pas la designation des
#   profils type D1 et D6"). Meme patron que LoadReferenceTable
#   (DataTable en lecture seule, donnees figees via le presenter).
# Comment il sera utilise :
# - interfaces/tui/app.py::action_help() (touche `a`, global).
# - interfaces/tui/screens/home.py (bouton "Aide").
# ---------------------------------------------------------------------->
