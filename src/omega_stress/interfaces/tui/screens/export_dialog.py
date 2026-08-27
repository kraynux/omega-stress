# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Export : choix du format, de la destination et du theme (HTML)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_stress.core.enums import ExportFormat
from omega_stress.core.results import Err
from omega_stress.interfaces.tui.controllers import history_controller
from omega_stress.interfaces.tui.presenters.theme_presenter import available_export_theme_names
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.settings_screen import DEFAULT_EXPORT_DIR_KEY

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer

_FORMAT_OPTIONS = [
    (ExportFormat.HTML.value, ExportFormat.HTML),
    (ExportFormat.CSV.value, ExportFormat.CSV),
    (ExportFormat.JSON.value, ExportFormat.JSON),
]
"""Ordre d'affichage volontairement DIFFERENT de la declaration de
ExportFormat (core/enums.py, JSON/CSV/HTML) : HTML en premier — donc
choix par defaut du Select ci-dessous, allow_blank=False — plutot que
JSON (bug/demande reelle, 2026-08-25 : "mettre en premier par defaut
html, puis cvs et json en choix secondaire et tertiaire"). Concerne
uniquement la presentation de CET ecran ; l'ordre de declaration de
l'enum lui-meme reste inchange (JSON/CSV/HTML), la seule autre
consommation de son ordre d'iteration (interfaces/cli/commands/
export_command.py, liste --help d'argparse) n'a pas de notion de
"defaut" a preserver."""


class ExportDialogScreen(OmegaScreen):
    """Formulaire d'export du rapport d'un run termine, identifie par
    run_id (voir screens/run_details.py, bouton "Exporter")."""

    def __init__(self, *, container: DependencyContainer, run_id: str) -> None:
        super().__init__()
        self._container = container
        self._run_id = run_id

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("EXPORTER LE RAPPORT", classes="omega-title")
            yield Select(
                _FORMAT_OPTIONS,
                prompt="Format",
                id="format",
                allow_blank=False,
                value=ExportFormat.HTML,
            )
            yield Input(placeholder="Dossier de destination", id="destination")
            yield Select(
                [(name, name) for name in available_export_theme_names()],
                prompt="Theme (HTML uniquement)",
                id="export-theme",
            )
            yield Static("", id="status")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter", id="export", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        default_dir = self._container.settings_store.get(
            DEFAULT_EXPORT_DIR_KEY, str(self._container.export_dir)
        )
        self.query_one("#destination", Input).value = default_dir or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "export":
            self.run_worker(self._export(), exclusive=True)

    async def _export(self) -> None:
        status = self.query_one("#status", Static)
        export_format = self.query_one("#format", Select).value
        destination_path = self.query_one("#destination", Input).value.strip()
        export_theme = self.query_one("#export-theme", Select).value

        if not isinstance(export_format, ExportFormat):
            status.update("Choisissez un format.")
            return
        if not destination_path:
            status.update("Indiquez un dossier de destination.")
            return
        theme_name = export_theme if isinstance(export_theme, str) else "omega-base"

        result = await history_controller.export_report(
            self._run_id,
            export_format=export_format,
            destination_path=destination_path,
            export_theme=theme_name,
            run_repository=self._container.run_repository,
            target_repository=self._container.target_repository,
            export_repository=self._container.export_repository,
            exporters=self._container.exporters,
        )
        if isinstance(result, Err):
            status.update(str(result.error))
            return
        status.update(f"Rapport ecrit : {result.value.written_path}")

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit le formulaire d'export en appel a
#   controllers/history_controller.py::export_report().
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Aucune serialisation JSON/CSV/HTML ici (deleguee a l'exporter concret
#   choisi par application/commands/export_run_report.py).
# Ce qu'il ne contient PAS :
# - Aucune verification que le run est termine : deja verifiee par
#   application/commands/export_run_report.py, relayee comme message
#   d'erreur si le run est encore en cours.
# Points cles :
# - "#format" (2026-08-25, demande reelle : "mettre en premier par
#   defaut html, puis cvs et json en choix secondaire et tertiaire") :
#   _FORMAT_OPTIONS ordonne explicitement HTML/CSV/JSON (voir son propre
#   commentaire) et value=ExportFormat.HTML force ce choix par defaut,
#   plutot que de compter sur le comportement de Select(allow_blank=False)
#   qui selectionne sa PREMIERE option de lui-meme (deja source d'un bug
#   different ailleurs, voir screens/settings_screen.py) — ici les deux
#   sont volontairement redondants et cohérents entre eux.
# - export_theme se replie sur "omega-base" si aucun choix n'est fait
#   (Select laisse a sa valeur vide) : coherent avec
#   application/dto/export_dto.py::ExportRequestDTO, meme valeur par
#   defaut — un choix de theme n'a de sens que pour le format HTML, ignore
#   silencieusement par les exporters JSON/CSV.
# - Options du Select "#export-theme" (2026-08-27, correction de bug reel)
#   : available_export_theme_names() (catalogue EXPORT_PALETTES, 5 noms),
#   PAS available_theme_names() (catalogue TUI_THEMES, 10 noms) — les deux
#   catalogues sont independants (domain/theme/policies.py). L'ancien code
#   proposait des noms de themes TUI-only invalides pour un export
#   (rejetes par validate_export_job()) et omettait les 2 themes
#   export-only (light-basic, light-alt).
# - "#destination" pre-rempli au montage (2026-08-24) avec
#   DEFAULT_EXPORT_DIR_KEY (importee de screens/settings_screen.py, une
#   seule source de verite pour le nom de cette cle settings_store —
#   c'est cet ecran qui l'expose en premier, le champ y est modifiable) :
#   avant ce correctif, l'utilisateur devait retaper un chemin a CHAQUE
#   export, le champ partant toujours vide. Reste modifiable ponctuellement
#   ici (une saisie ici n'est jamais persistee comme nouveau reglage
#   global : seul le champ homonyme de screens/settings_screen.py,
#   sauve au blur/validation, met a jour DEFAULT_EXPORT_DIR_KEY).
# Comment il sera utilise :
# - interfaces/tui/screens/run_details.py (bouton "Exporter").
#---------------------------------------------------------------------->
