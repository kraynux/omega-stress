# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Selection d'une cible : liste epinglee/recente, ou saisie manuelle."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Label, OptionList
from textual.widgets.option_list import Option

from omega_stress.application.dto.target_dto import TargetDTO


class TargetPicker(Vertical):
    """Combine une liste de cibles connues et un champ de saisie libre."""

    def compose(self) -> ComposeResult:
        yield Label("Cible", classes="omega-subtitle")
        yield OptionList(id="known-targets")
        yield Input(
            placeholder="ou saisir une adresse (ex. https://exemple.org)",
            id="manual-target",
        )

    def load_targets(self, targets: tuple[TargetDTO, ...]) -> None:
        option_list = self.query_one("#known-targets", OptionList)
        option_list.clear_options()
        for target in targets:
            marker = "* " if target.pinned else "  "
            option_list.add_option(Option(f"{marker}{target.base_url}", id=target.id))

    @property
    def manual_value(self) -> str:
        return self.query_one("#manual-target", Input).value

    @manual_value.setter
    def manual_value(self, value: str) -> None:
        self.query_one("#manual-target", Input).value = value

# <-- INFO DEV ---------------------------------------------------------
# Role : composant de choix de cible reutilise par les 3 ecrans de
# lancement (request/connection/ramp).
# Pourquoi dans interfaces/tui/widgets/ (charte) : pas de validation
# metier ici — l'adresse saisie est validee par
# application/commands/run_precheck.py (via domain/target/policies.py),
# jamais dans l'interface.
# Ce qu'il ne contient PAS : le marqueur "*" est en ASCII pur (pas
# d'emoji) pour rester lisible aussi en profil `mono`/`reduced`.
# Points cles : le setter de manual_value (2026-08-24) permet a un ecran
# de PRE-REMPLIR le champ (ex. cible par defaut d'un profil fige
# selectionne) sans connaitre l'id interne "#manual-target" — seule cette
# classe sait ou vit reellement le champ de saisie libre.
# Comment il sera utilise : screens/request_panel.py, connection_panel.py,
# ramp_panel.py, profile_wizard.py.
#---------------------------------------------------------------------->
