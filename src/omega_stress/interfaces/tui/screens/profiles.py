# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Profils : liste, creation, gel et suppression des profils de test."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_stress.core.results import Err
from omega_stress.interfaces.tui.controllers import profile_controller
from omega_stress.interfaces.tui.presenters.profile_presenter import status_label
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.confirm import ConfirmScreen
from omega_stress.interfaces.tui.screens.profile_wizard import ProfileWizardScreen
from omega_stress.interfaces.tui.widgets.profile_list import ProfileList

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer


class ProfilesScreen(OmegaScreen):
    """Liste les profils existants ; permet d'en creer un nouveau
    (assistant, profile_wizard.py), de figer ou de supprimer le profil
    selectionne."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_profile_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("PROFILS", classes="omega-title")
            yield ProfileList(id="profiles")
            yield Static("", id="status")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Nouveau profil", id="new-profile", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Figer le profil selectionne", id="freeze-profile")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer le profil selectionne", id="delete-profile")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        profiles = profile_controller.load_profiles(
            profile_repository=self._container.profile_repository
        )
        self.query_one(ProfileList).load_profiles(profiles)
        if profiles:
            self._select(profiles[0].id)
        else:
            self._selected_profile_id = None

    def _select(self, profile_id: str | None) -> None:
        self._selected_profile_id = profile_id
        if profile_id is None:
            return
        for profile in profile_controller.load_profiles(
            profile_repository=self._container.profile_repository
        ):
            if profile.id == profile_id:
                self.query_one("#status", Static).update(
                    f"{profile.name} — {status_label(profile)}"
                )
                break

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._select(event.row_key.value)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._select(event.row_key.value)

    def on_screen_resume(self) -> None:
        self._refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "new-profile":
            self.app.push_screen(ProfileWizardScreen(container=self._container))
        elif event.button.id == "freeze-profile":
            self._freeze_selected()
        elif event.button.id == "delete-profile":
            self._confirm_delete_selected()

    def _freeze_selected(self) -> None:
        status_widget = self.query_one("#status", Static)
        if self._selected_profile_id is None:
            status_widget.update("Selectionnez d'abord un profil.")
            return
        result = profile_controller.freeze(
            self._selected_profile_id, profile_repository=self._container.profile_repository
        )
        if isinstance(result, Err):
            status_widget.update(str(result.error))
            return
        status_widget.update(f"{result.value.name} fige.")
        self._refresh()

    def _confirm_delete_selected(self) -> None:
        if self._selected_profile_id is None:
            self.query_one("#status", Static).update("Selectionnez d'abord un profil.")
            return
        self.app.push_screen(
            ConfirmScreen(
                title="SUPPRIMER CE PROFIL ?",
                message=(
                    "Definitif. Un run passe lie a ce profil ne pourra plus etre rejoue."
                ),
            ),
            self._delete_selected_if_confirmed,
        )

    def _delete_selected_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed or self._selected_profile_id is None:
            return
        profile_controller.delete(
            self._selected_profile_id, profile_repository=self._container.profile_repository
        )
        self.query_one("#status", Static).update("Profil supprime.")
        self._refresh()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Ecran de gestion des profils : lecture (liste), creation (assistant),
#   gel, suppression.
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Delegue tout a controllers/profile_controller.py, qui applique deja le
#   tri d'affichage (favoris d'abord). Meme principe pour la suppression :
#   delegue au controller, demande seulement la confirmation
#   (screens/confirm.py) avant d'appeler.
# Ce qu'il ne contient PAS :
# - Aucune construction de Profile ni validation (voir
#   domain/profiles/validation.py, relayee par le controller).
# Points cles :
# - on_screen_resume() rafraichit la liste au retour de
#   profile_wizard.py : necessaire car ce dernier cree un profil pendant
#   que cet ecran reste en pile (push_screen, pas de remplacement).
# - _selected_profile_id vit uniquement en memoire d'ecran (jamais
#   persiste) : redemande a chaque nouvelle selection de ligne.
# - on_data_table_row_highlighted() (2026-08-24, ajoute a cote de
#   on_data_table_row_selected()) : DataTable positionne son curseur sur
#   la premiere ligne des le chargement, sans emettre RowSelected (cet
#   evenement n'arrive que sur activation explicite, Entree ou double-clic)
#   — un simple clic sur une ligne DEJA en position de curseur (le cas le
#   plus frequent : la ligne la plus recente/pertinente est deja
#   surlignee par defaut) ne changeait donc jamais _selected_profile_id,
#   laissant "Figer"/"Supprimer" silencieusement inoperants. RowHighlighted
#   se declenche sur tout changement de curseur (clic ou fleches), corrige
#   la cause reelle plutot que son seul symptome. _refresh() initialise
#   aussi explicitement la selection sur la premiere ligne (meme raison :
#   DataTable ne notifie personne de son propre positionnement initial).
# - Suppression (2026-08-24) : delete() de domain n'interdit pas un profil
#   fige (frozen empeche seulement une modification ulterieure, pas la
#   suppression, voir application/commands/delete_profile.py) — le message
#   de confirmation avertit explicitement de la consequence sur
#   "Rejouer" (screens/history.py) pour un run passe lie a ce profil.
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Profils").
#---------------------------------------------------------------------->
