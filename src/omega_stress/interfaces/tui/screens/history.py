# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Historique : liste des runs passes, detail et relecture."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_stress.core.results import Err
from omega_stress.interfaces.tui.controllers import history_controller, load_controller
from omega_stress.interfaces.tui.presenters.run_presenter import verdict_label
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.export_dialog import ExportDialogScreen
from omega_stress.interfaces.tui.screens.run_details import RunDetailsScreen
from omega_stress.interfaces.tui.widgets.history_table import HistoryTable
from omega_stress.interfaces.tui.widgets.notification_bar import NotificationBar

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer


class HistoryScreen(OmegaScreen):
    """Liste les runs passes ; permet d'en voir le detail ou de rejouer
    le run selectionne (uniquement s'il reference un profil fige, voir
    domain/runs/validators.py::can_be_replayed)."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_run_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("HISTORIQUE", classes="omega-title")
            yield HistoryTable(id="history")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir le detail", id="details")
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter", id="export")
                with Container(classes="omega-btn-frame"):
                    yield Button("Rejouer", id="replay", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
            yield NotificationBar(id="notifications")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def on_screen_resume(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        runs = history_controller.load_history(
            run_repository=self._container.run_repository,
            target_repository=self._container.target_repository,
        )
        self.query_one(HistoryTable).load_runs(runs)
        self._selected_run_id = runs[0].id if runs else None

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_run_id = event.row_key.value

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._selected_run_id = event.row_key.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "details" and self._selected_run_id is not None:
            self.app.push_screen(
                RunDetailsScreen(container=self._container, run_id=self._selected_run_id)
            )
        elif event.button.id == "export" and self._selected_run_id is not None:
            self.app.push_screen(
                ExportDialogScreen(container=self._container, run_id=self._selected_run_id)
            )
        elif event.button.id == "replay" and self._selected_run_id is not None:
            self.run_worker(self._replay(self._selected_run_id), exclusive=True)

    async def _replay(self, run_id: str) -> None:
        notification_bar = self.query_one(NotificationBar)
        result = await load_controller.launch_replay(
            run_id,
            container=self._container,
            explicit_confirmation=False,
            precheck_validated=False,
            run_progress_notifier=_NoOpProgressNotifier(),
            notification_sink=notification_bar,
        )
        if isinstance(result, Err):
            notification_bar(str(result.error))
            return
        notification_bar(f"Relance terminee : {verdict_label(result.value)}")
        self._refresh()


class _NoOpProgressNotifier:
    """Absorbe la progression d'une relecture : cet ecran n'affiche pas de
    ProgressPanel (voir Points cles), contrairement aux ecrans de
    lancement direct (request_panel.py et consorts)."""

    def notify(self, run_id: str, sample: object) -> None:
        return None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Liste l'historique et permet trois actions sur le run selectionne :
#   voir le detail, l'exporter directement, ou le rejouer (relance depuis
#   son profil fige d'origine).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Delegue tout a controllers/history_controller.py (lecture) et
#   controllers/load_controller.py (relecture), aucune regle metier propre.
# Ce qu'il ne contient PAS :
# - Aucune barre de progression pour la relecture (_NoOpProgressNotifier
#   absorbe silencieusement les IntervalSample) : contrairement aux trois
#   ecrans de lancement direct, cet ecran privilegie la simplicite (une
#   relecture est une action secondaire, rarement suivie en direct).
# Points cles :
# - explicit_confirmation=False passe a launch_replay() : une relecture
#   ne recree jamais de confirmation d'autorisation ponctuelle — soit la
#   cible d'origine est deja epinglee (guard passe), soit elle ne l'est
#   plus et la relecture est refusee avec un message explicite, jamais un
#   contournement silencieux de la regle d'autorisation.
# - on_screen_resume() rafraichit la liste au retour de
#   run_details.py/export_dialog.py, pour refleter un eventuel export.
# - on_data_table_row_highlighted() (2026-08-24, ajoute a cote de
#   on_data_table_row_selected()) : bug reel rapporte ("un nouveau test
#   libre, je ne peux pas afficher le detail ni exporter") — reproduit et
#   confirme : DataTable surligne sa premiere ligne des le chargement
#   (toujours le run le PLUS RECENT ici, tri le plus recent d'abord) sans
#   emettre RowSelected (evenement reserve a une activation explicite,
#   Entree ou double-clic) ; un simple clic sur cette ligne DEJA en
#   position de curseur ne change donc rien et ne declenche AUCUN
#   evenement, laissant _selected_run_id a None indefiniment pour le run
#   qu'un utilisateur veut le plus souvent consulter juste apres l'avoir
#   lance. RowHighlighted se declenche sur tout changement de curseur
#   (clic ou fleches) : corrige la cause reelle. _refresh() initialise
#   aussi explicitement la selection sur le premier run (meme raison :
#   DataTable ne notifie personne de son propre positionnement initial).
# - Bouton "Exporter" (2026-08-24) : pousse ExportDialogScreen directement
#   sur la selection courante, sans passer par "Voir le detail" — avant ce
#   correctif, RunDetailsScreen etait le SEUL point d'entree de l'export
#   depuis l'historique, un detour supplementaire pour l'action la plus
#   frequente depuis cet ecran (voir aussi screens/run_details.py, ou le
#   bouton "Exporter" d'origine reste inchange).
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Historique").
#---------------------------------------------------------------------->
