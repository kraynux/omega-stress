# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Reglages : theme TUI et profil de rendu (auto ou force)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_stress.interfaces.tui.controllers import (
    history_controller,
    load_controller,
    render_profile_controller,
    theme_controller,
)
from omega_stress.interfaces.tui.presenters.theme_presenter import (
    available_theme_names,
    status_label,
)
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.confirm import ConfirmScreen
from omega_stress.interfaces.tui.widgets.render_profile_badge import RenderProfileBadge
from omega_stress.interfaces.tui.widgets.theme_badge import ThemeBadge

if TYPE_CHECKING:
    # Voir interfaces/cli/commands/run_command.py pour la justification
    # complete de ce motif (exclude_type_checking_imports).
    from omega_stress.app.dependency_container import DependencyContainer

_RENDER_PROFILE_OPTIONS: list[tuple[str, RenderProfile | None]] = [
    ("Automatique", None),
    *((profile.value, profile) for profile in RenderProfile),
]

DEFAULT_EXPORT_DIR_KEY = "default_export_dir"
"""Cle settings_store partagee avec screens/export_dialog.py (meme
prefill), voir son propre INFO DEV."""

DEFAULT_SCREENSHOT_DIR_KEY = "default_screenshot_dir"
"""Cle settings_store partagee avec interfaces/tui/app.py (commande
"Capture d'ecran" de la palette) — meme patron que DEFAULT_EXPORT_DIR_KEY,
voir son propre INFO DEV."""


class SettingsScreen(OmegaScreen):
    """Permet de changer de theme (10 au choix) et de forcer un profil de
    rendu different de l'auto-detection (mode manuel)."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        current_theme = self.app.theme
        stored_profile_raw = self._container.settings_store.get("render_profile")
        current_profile = RenderProfile(stored_profile_raw) if stored_profile_raw else None
        with Vertical(classes="omega-panel"):
            yield Static("REGLAGES", classes="omega-title")
            yield Static("Theme", classes="omega-subtitle")
            yield ThemeBadge(current_theme, id="theme-badge")
            yield Select(
                [(name, name) for name in available_theme_names()],
                id="theme-select",
                allow_blank=False,
                value=current_theme,
            )
            yield Static("Profil de rendu", classes="omega-subtitle")
            yield RenderProfileBadge(current_profile, id="render-profile-badge")
            yield Select(
                _RENDER_PROFILE_OPTIONS,
                id="render-profile-select",
                allow_blank=False,
                value=current_profile,
            )
            yield Static("Export", classes="omega-subtitle")
            yield Input(placeholder="Dossier d'export par defaut", id="default-export-dir")
            yield Static("Captures d'ecran", classes="omega-subtitle")
            yield Input(
                placeholder="Dossier des captures d'ecran par defaut",
                id="default-screenshot-dir",
            )
            yield Static("Cibles", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Vider les cibles recentes", id="clear-recent-targets")
                with Container(classes="omega-btn-frame"):
                    yield Button(
                        "Effacer toutes les cibles", id="clear-all-targets", variant="error"
                    )
            yield Static("Historique", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Vider l'historique", id="clear-history", variant="error")
            yield Static("", id="settings-status")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        default_dir = self._container.settings_store.get(
            DEFAULT_EXPORT_DIR_KEY, str(self._container.export_dir)
        )
        self.query_one("#default-export-dir", Input).value = default_dir or ""
        default_screenshot_dir = self._container.settings_store.get(
            DEFAULT_SCREENSHOT_DIR_KEY, str(self._container.screenshot_dir)
        )
        self.query_one("#default-screenshot-dir", Input).value = default_screenshot_dir or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "clear-recent-targets":
            self.app.push_screen(
                ConfirmScreen(
                    title="VIDER LES CIBLES RECENTES ?",
                    message="Les cibles epinglees ne sont pas concernees.",
                ),
                self._clear_recent_targets_if_confirmed,
            )
        elif event.button.id == "clear-all-targets":
            self.app.push_screen(
                ConfirmScreen(
                    title="EFFACER TOUTES LES CIBLES ?",
                    message=(
                        "Y compris les cibles epinglees : les autorisations "
                        "deja accordees seront perdues."
                    ),
                ),
                self._clear_all_targets_if_confirmed,
            )
        elif event.button.id == "clear-history":
            self.app.push_screen(
                ConfirmScreen(
                    title="VIDER L'HISTORIQUE ?",
                    message="Tous les runs enregistres seront effaces definitivement.",
                ),
                self._clear_history_if_confirmed,
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "default-export-dir":
            self._save_default_export_dir(event.value)
        elif event.input.id == "default-screenshot-dir":
            self._save_default_screenshot_dir(event.value)

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "default-export-dir":
            self._save_default_export_dir(event.value)
        elif event.input.id == "default-screenshot-dir":
            self._save_default_screenshot_dir(event.value)

    def _save_default_export_dir(self, value: str) -> None:
        self._container.settings_store.set(DEFAULT_EXPORT_DIR_KEY, value.strip())

    def _save_default_screenshot_dir(self, value: str) -> None:
        self._container.settings_store.set(DEFAULT_SCREENSHOT_DIR_KEY, value.strip())

    def _clear_recent_targets_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        load_controller.clear_recent_targets(target_repository=self._container.target_repository)
        self.query_one("#settings-status", Static).update("Cibles recentes videes.")

    def _clear_all_targets_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        load_controller.clear_all_targets(target_repository=self._container.target_repository)
        self.query_one("#settings-status", Static).update("Toutes les cibles ont ete effacees.")

    def _clear_history_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        history_controller.clear_run_history(run_repository=self._container.run_repository)
        self.query_one("#settings-status", Static).update("Historique vide.")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme-select" and isinstance(event.value, str):
            self._apply_theme(event.value)
        elif event.select.id == "render-profile-select":
            self._apply_render_profile(event.value)

    def _apply_theme(self, theme_name: str) -> None:
        current_profile = RenderProfile(
            self._container.settings_store.get("render_profile", RenderProfile.STANDARD.value)
        )
        status = theme_controller.choose_theme(
            theme_name,
            render_profile=current_profile,
            settings_store=self._container.settings_store,
        )
        self.app.theme = status.theme_name
        self.query_one("#theme-badge", ThemeBadge).update_theme(status_label(status))

    def _apply_render_profile(self, manual_override: object) -> None:
        override = manual_override if isinstance(manual_override, RenderProfile) else None
        status = render_profile_controller.apply_render_profile(
            terminal_detector=self._container.terminal_detector,
            settings_store=self._container.settings_store,
            manual_override=override,
        )
        self.query_one("#render-profile-badge", RenderProfileBadge).update_profile(
            RenderProfile(status.render_profile)
        )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree utilisateur unique pour changer de theme ou forcer un
#   profil de rendu (mode manuel), en dehors du raccourci clavier global
#   `t` (voir app.py) reserve au cyclage rapide du theme.
# - Depuis le 2026-08-24, egalement point d'entree unique pour : le
#   dossier d'export par defaut, et les trois purges destructrices
#   (cibles recentes, toutes les cibles, historique des runs).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Delegue tout a controllers/theme_controller.py et
#   controllers/render_profile_controller.py, ne decide jamais lui-meme
#   d'une regle (repli de theme, degradation de profil). Meme principe
#   pour les purges : delegue a load_controller.py (cibles) et
#   history_controller.py (runs), demande seulement la confirmation
#   (screens/confirm.py) avant d'appeler l'un ou l'autre.
# Ce qu'il ne contient PAS :
# - Aucune reconstruction de Theme Textual ni de stylesheet : les 10
#   themes sont deja tous enregistres au demarrage par app.py
#   (register_theme() pour chacun), cet ecran se contente d'activer
#   `self.app.theme = status.theme_name` (l'API Textual standard pour
#   basculer entre themes deja enregistres) et de persister le choix.
# Ce qu'il contenait a tort jusqu'au 2026-08-24 :
# - _apply_theme() ne faisait QUE persister et rafraichir le badge,
#   jamais `self.app.theme = ...` : le theme choisi ici n'avait donc
#   d'effet visuel qu'au PROCHAIN demarrage (resolve_startup_state() le
#   relit alors depuis settings_store), jamais sur l'ecran courant — a la
#   difference du raccourci clavier `t` (app.py::action_cycle_theme), qui
#   l'a toujours fait correctement. Aucune observation de settings_store
#   par app.py n'a jamais existe ; l'ancien commentaire ci-dessus le
#   supposait a tort.
# Points cles :
# - "Automatique" (valeur None dans _RENDER_PROFILE_OPTIONS) reappelle
#   apply_render_profile() sans manual_override : redecouvre le profil
#   auto-detecte a la demande, sans jamais le cacher en dur ici.
# - #theme-select/#render-profile-select construits avec `value=...`
#   directement dans compose() (2026-08-25, bug reel rapporte : "je
#   retourne dans reglages, il est toujours sur automatique, quel que
#   soit le profil choisi, et rien ne s'affiche en ascii") — avant ce
#   correctif, aucun des deux Select ne recevait de valeur initiale,
#   donc chacun retombait sur sa PREMIERE option ("Automatique"/None pour
#   le profil, premier theme alphabetique pour le theme) a chaque
#   nouvelle visite, quel que soit l'etat reellement persiste. Un premier
#   correctif (assigner `.value` APRES coup dans on_mount(), sous
#   `self.prevent(Select.Changed)`) s'est revele insuffisant : Select
#   (allow_blank=False) selectionne deja sa PROPRE premiere option
#   ("Automatique"/None) et poste son evenement Changed pendant son
#   propre montage, AVANT que le on_mount() du Screen parent ne s'execute
#   — prevent() ne pouvait donc pas suppimer cet evenement precoce
#   (verifie : `on_select_changed` recevait bien ('render-profile-select',
#   None) avant meme que la correction n'ait pu s'appliquer), qui
#   appelait _apply_render_profile(None) et retombait sur l'auto-detection,
#   EFFACANT silencieusement la valeur persistee reelle (settings_store
#   finissait toujours sur le profil auto-detecte, jamais celui choisi).
#   Passer `value=` directement au CONSTRUCTEUR du Select evite qu'il ait
#   jamais besoin de choisir lui-meme une premiere option par defaut :
#   aucun evenement Changed parasite ne peut se produire, le probleme est
#   evite a la source plutot que rattrape apres coup. settings_store ne
#   distingue pas "auto resolu vers X" de "force manuellement vers X" :
#   ce Select ne peut donc afficher que le profil ACTUELLEMENT actif, pas
#   le mode qui l'a produit — limitation acceptee, sans rapport avec le
#   bug rapporte.
# - "#default-export-dir" (2026-08-24) : pre-rempli au montage avec
#   settings_store.get(DEFAULT_EXPORT_DIR_KEY, str(container.export_dir))
#   — la valeur par defaut (avant toute personnalisation) est
#   container.export_dir, resolu une seule fois par
#   app/dependency_container.py (voir son propre INFO DEV, cette classe
#   n'importe jamais infrastructure/config/paths.py directement). Sauve
#   au blur ET a la validation (Enter) : les deux evenements appellent le
#   meme _save_default_export_dir(), aucune duplication de logique.
#   DEFAULT_EXPORT_DIR_KEY est exportee (pas prefixee _) car
#   screens/export_dialog.py lit la meme cle pour pre-remplir son propre
#   champ "Dossier de destination" — une seule source de verite pour le
#   nom de la cle.
# - "#default-screenshot-dir" (2026-08-25, bug reel rapporte : "rajouter
#   dans les reglages... la possibilite de modifier le chemin des
#   captures") : meme patron EXACT que "#default-export-dir" ci-dessus
#   (prefill container.screenshot_dir, sauve au blur/validation via
#   DEFAULT_SCREENSHOT_DIR_KEY, exportee pour la meme raison — lue ici
#   par interfaces/tui/app.py au moment de livrer une capture d'ecran,
#   voir son propre INFO DEV).
# - Les trois purges (2026-08-24) suivent toutes le meme patron : bouton
#   -> ConfirmScreen(title, message) -> callback qui n'agit QUE si
#   confirmed est True -> controller -> message dans #settings-status.
#   Aucune des trois n'a d'effet si l'utilisateur annule (confirmed est
#   False ou None selon comment l'ecran de confirmation a ete quitte).
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Reglages"),
#   interfaces/tui/app.py (raccourci clavier `t`, chemin rapide distinct).
#---------------------------------------------------------------------->
