# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Cibles : liste, epinglage et desepinglage."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_stress.core.results import Err
from omega_stress.interfaces.tui.controllers import load_controller
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.widgets.authorization_checkbox import AuthorizationCheckbox
from omega_stress.interfaces.tui.widgets.target_table import TargetTable

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer


class TargetsScreen(OmegaScreen):
    """Liste les cibles (epinglees et recentes) ; permet d'epingler une
    nouvelle adresse ou de desepingler la cible selectionnee."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_target_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("CIBLES", classes="omega-title")
            yield Static(
                "Cibles epinglees : illimitees | Cibles recentes : 10 maximum",
                classes="omega-subtitle",
            )
            yield TargetTable(id="targets")
            yield Static("", id="status")
            yield Input(placeholder="Nouvelle adresse (ex. https://exemple.org)", id="new-address")
            yield AuthorizationCheckbox(id="authorization")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Epingler", id="pin", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Desepingler la cible selectionnee", id="unpin")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def on_screen_resume(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        targets = load_controller.load_targets(target_repository=self._container.target_repository)
        self.query_one(TargetTable).load_targets(targets)
        self._selected_target_id = targets[0].id if targets else None

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_target_id = event.row_key.value

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._selected_target_id = event.row_key.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "pin":
            self._pin()
        elif event.button.id == "unpin":
            self._unpin()

    def _pin(self) -> None:
        status = self.query_one("#status", Static)
        raw_address = self.query_one("#new-address", Input).value.strip()
        if not raw_address:
            status.update("Saisissez une adresse a epingler.")
            return
        result = load_controller.pin_new_target(
            target_repository=self._container.target_repository,
            raw_address=raw_address,
            authorization_confirmed=self.query_one(AuthorizationCheckbox).value,
        )
        if isinstance(result, Err):
            status.update(str(result.error))
            return
        status.update(f"{result.value.base_url} epinglee.")
        self.query_one("#new-address", Input).value = ""
        self.query_one(AuthorizationCheckbox).value = False
        self._refresh()

    def _unpin(self) -> None:
        status = self.query_one("#status", Static)
        if self._selected_target_id is None:
            status.update("Selectionnez d'abord une cible.")
            return
        load_controller.unpin_existing_target(
            self._selected_target_id, target_repository=self._container.target_repository
        )
        status.update("Cible desepinglee.")
        self._selected_target_id = None
        self._refresh()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul ecran permettant d'epingler/desepingler une cible — jusqu'a ce
#   correctif (2026-08-24), application/commands/pin_target.py et
#   unpin_target.py existaient et etaient deja exposes par
#   controllers/load_controller.py (pin_new_target()/
#   unpin_existing_target()), mais AUCUN ecran ne les appelait : la case
#   d'autorisation devait donc toujours etre recochee a chaque lancement,
#   et widgets/target_picker.py restait toujours vide de cibles connues
#   (rien ne les y faisait jamais apparaitre).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Delegue tout a controllers/load_controller.py, deja construit pour
#   cet usage precis (voir son INFO DEV, "Aucun target_controller.py
#   dedie... rejoignent naturellement ce controller").
# Ce qu'il ne contient PAS :
# - Aucune regle d'autorisation propre : domain/targets/service.py::pin()
#   refuse deja sans confirmation, ce formulaire ne fait que relayer le
#   refus tel quel dans #status, exactement comme les 3 ecrans de
#   lancement le font deja pour authorization_guard.py.
# Points cles :
# - "Desepingler" agit sur la ligne SELECTIONNEE de TargetTable (cibles
#   epinglees et recentes melangees, meme liste que widgets/
#   target_picker.py) : desepingler une cible deja "recente" (non
#   epinglee) est un no-op silencieux cote
#   application/commands/unpin_target.py (voir son INFO DEV), pas une
#   erreur ici.
# - on_screen_resume() rafraichit la liste, meme convention que
#   screens/profiles.py.
# - on_data_table_row_highlighted() (2026-08-24) : meme correctif et meme
#   raison que screens/history.py (voir son INFO DEV pour le bug complet)
#   — un simple clic sur la ligne DEJA en position de curseur par defaut
#   (la premiere) ne declenchait aucun evenement, laissant "Desepingler"
#   silencieusement inoperant sur la cible la plus visible de la liste.
# - Legende "epinglees : illimitees | recentes : 10 maximum" (2026-08-24) :
#   valeur en dur coherente avec application/queries/list_targets.py::
#   list_targets(recent_limit=10, valeur par defaut) — pas lue
#   dynamiquement depuis la query (elle ne l'expose pas comme donnee, ce
#   n'est qu'un parametre par defaut), a mettre a jour manuellement si ce
#   defaut change un jour. Repond a la question posee explicitement par
#   l'utilisateur ("a combien sont-elles au max d'affichage").
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Cibles").
#---------------------------------------------------------------------->
