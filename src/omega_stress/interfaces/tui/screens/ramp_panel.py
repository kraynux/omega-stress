# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de lancement d'un Test charge (montee progressive)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, OptionList, Select, Static
from textual.worker import Worker

from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.load.policies import allowed_durations_minutes, is_precheck_mandatory
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.interfaces.tui.controllers import load_controller, profile_controller
from omega_stress.interfaces.tui.presenters.run_presenter import verdict_label
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.run_details import RunDetailsScreen
from omega_stress.interfaces.tui.widgets.authorization_checkbox import AuthorizationCheckbox
from omega_stress.interfaces.tui.widgets.notification_bar import NotificationBar
from omega_stress.interfaces.tui.widgets.progress_panel import ProgressPanel
from omega_stress.interfaces.tui.widgets.run_progress import RunProgress
from omega_stress.interfaces.tui.widgets.target_picker import TargetPicker

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer

_LEVEL_OPTIONS = [(level.value, level) for level in IntensityLevel]
_MAX_ERROR_RATE_OPTIONS = [(f"{v / 10:.1f}", v / 10) for v in range(11)]
_DEFAULT_DURATION_OPTIONS = [
    (f"{m} min", m) for m in allowed_durations_minutes(IntensityLevel.BAS)
]
"""Voir screens/request_panel.py, meme raison (EmptySelectError sinon)."""


class _PanelProgressNotifier:
    """Voir screens/request_panel.py::_PanelProgressNotifier, meme
    adaptateur, duplique ici a l'identique (pas de fichier partage listed
    dans ARCHITECTURE.md §2 pour ces trois ecrans de lancement)."""

    def __init__(self, panel: ProgressPanel, progress: RunProgress) -> None:
        self._panel = panel
        self._progress = progress

    def notify(self, run_id: str, sample: IntervalSample) -> None:
        self._panel.update_sample(sample)
        self._progress.update_elapsed(sample.at_second)


class RampPanelScreen(OmegaScreen):
    """Formulaire de lancement d'un Test charge en mode manuel borne."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_target: TargetDTO | None = None
        self._targets_by_index: dict[int, TargetDTO] = {}
        self._selected_profile_id: str | None = None
        self._precheck_validated: bool = False
        self._active_worker: Worker[None] | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("TEST CHARGE", classes="omega-title")
            yield Select([], prompt="Profil fige (optionnel)", id="profile")
            yield TargetPicker(id="target-picker")
            yield Static("Criteres du test", classes="omega-subtitle")
            yield Select(_LEVEL_OPTIONS, prompt="Intensite", id="level", allow_blank=False)
            yield Select(
                _DEFAULT_DURATION_OPTIONS,
                prompt="Duree (minutes)",
                id="duration",
                allow_blank=False,
            )
            yield Select(
                _MAX_ERROR_RATE_OPTIONS,
                prompt="Taux d'erreur maximal",
                id="max-error-rate",
                allow_blank=False,
            )
            yield AuthorizationCheckbox(id="authorization")
            with Horizontal(classes="omega-actions"):
                with Container(id="precheck-frame", classes="omega-btn-frame"):
                    yield Button("Pre-check", id="precheck")
                with Container(classes="omega-btn-frame"):
                    yield Button("Lancer", id="launch", variant="primary")
                with Container(id="stop-frame", classes="omega-btn-frame"):
                    yield Button("Arreter", id="stop", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
            yield RunProgress(id="run-progress")
            yield ProgressPanel(id="progress")
            yield NotificationBar(id="notifications")
            yield Static("", id="result")
        yield Footer()

    def on_mount(self) -> None:
        targets = load_controller.load_targets(target_repository=self._container.target_repository)
        self._targets_by_index = dict(enumerate(targets))
        self.query_one(TargetPicker).load_targets(targets)

        frozen_profiles = [
            p
            for p in profile_controller.load_profiles(
                profile_repository=self._container.profile_repository
            )
            if p.frozen and p.family == TestFamily.RAMP.value
        ]
        self.query_one("#profile", Select).set_options((p.name, p) for p in frozen_profiles)
        self._set_duration_options(IntensityLevel.BAS)
        self.query_one("#precheck-frame", Container).display = False
        self.query_one("#stop-frame", Container).display = False

    def _set_duration_options(
        self, level: IntensityLevel, *, keep_value: int | None = None
    ) -> None:
        """Voir screens/request_panel.py, meme logique a l'identique."""
        options = allowed_durations_minutes(level)
        duration_select = self.query_one("#duration", Select)
        duration_select.set_options((f"{m} min", m) for m in options)
        if keep_value is not None and keep_value in options:
            duration_select.value = keep_value
        else:
            duration_select.value = options[0]
            if keep_value is not None:
                self.query_one("#result", Static).update(
                    f"Duree ramenee a {options[0]} min : {level.value} "
                    f"ne propose pas {keep_value} min."
                )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._selected_target = self._targets_by_index.get(event.option_index)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "level" and isinstance(event.value, IntensityLevel):
            current_duration = self.query_one("#duration", Select).value
            self._set_duration_options(
                event.value,
                keep_value=current_duration if isinstance(current_duration, int) else None,
            )
            self.query_one("#precheck-frame", Container).display = is_precheck_mandatory(
                event.value
            )
            return
        if event.select.id != "profile":
            return
        profile = event.value
        if not isinstance(profile, ProfileDTO):
            self._selected_profile_id = None
            return
        self._apply_profile(profile)

    def _apply_profile(self, profile: ProfileDTO) -> None:
        self._selected_profile_id = profile.id
        level = IntensityLevel(profile.level)
        self.query_one("#level", Select).value = level
        self._set_duration_options(level, keep_value=profile.duration_minutes)
        self.query_one("#max-error-rate", Select).value = profile.max_error_rate

        matching_target = next(
            (t for t in self._targets_by_index.values() if t.id == profile.default_target_id),
            None,
        )
        if matching_target is not None:
            self._selected_target = matching_target
            self.query_one(TargetPicker).manual_value = ""
        else:
            self.query_one(TargetPicker).manual_value = profile.default_target_id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "launch":
            self._active_worker = self.run_worker(self._launch(), exclusive=True)
        elif event.button.id == "precheck":
            self._active_worker = self.run_worker(self._run_precheck(), exclusive=True)
        elif event.button.id == "stop" and self._active_worker is not None:
            self._active_worker.cancel()

    async def _run_precheck(self) -> None:
        result_label = self.query_one("#result", Static)
        target = self._resolve_target()
        if target is None:
            result_label.update("Choisissez ou saisissez une cible avant le pre-check.")
            return
        target_id, target_url = target

        result_label.update("Pre-check en cours…")
        run_progress = self.query_one(RunProgress)
        run_progress.start(total_seconds=60)
        self.query_one("#stop-frame", Container).display = True
        outcome = await load_controller.launch_precheck(
            container=self._container,
            target_id=target_id,
            target_url=target_url,
            explicit_confirmation=self.query_one(AuthorizationCheckbox).value,
            run_progress_notifier=_PanelProgressNotifier(
                self.query_one(ProgressPanel), run_progress
            ),
            notification_sink=self.query_one(NotificationBar),
        )
        run_progress.stop()
        self.query_one("#stop-frame", Container).display = False

        self._precheck_validated = not isinstance(outcome, Err)
        if isinstance(outcome, Err):
            result_label.update(f"Pre-check echoue : {outcome.error}")
            return
        result_label.update(
            f"Pre-check reussi ({verdict_label(outcome.value)}) — vous pouvez lancer le test."
        )

    def _resolve_target(self) -> tuple[str, str] | None:
        manual_value = self.query_one(TargetPicker).manual_value.strip()
        if manual_value:
            return manual_value, manual_value
        if self._selected_target is not None:
            return self._selected_target.id, self._selected_target.base_url
        return None

    async def _launch(self) -> None:
        result_label = self.query_one("#result", Static)
        result_label.update("Lancement en cours…")
        target = self._resolve_target()
        if target is None:
            result_label.update("Choisissez ou saisissez une cible.")
            return
        target_id, target_url = target

        level = self.query_one("#level", Select).value
        if not isinstance(level, IntensityLevel):
            result_label.update("Choisissez un niveau d'intensite.")
            return

        duration_minutes = self.query_one("#duration", Select).value
        max_error_rate = self.query_one("#max-error-rate", Select).value
        if not isinstance(duration_minutes, int) or not isinstance(max_error_rate, float):
            result_label.update("Choisissez une duree et un taux d'erreur.")
            return

        run_progress = self.query_one(RunProgress)
        run_progress.start(total_seconds=duration_minutes * 60)
        self.query_one("#stop-frame", Container).display = True
        outcome = await load_controller.launch_ramp(
            container=self._container,
            target_id=target_id,
            target_url=target_url,
            level=level,
            duration_minutes=duration_minutes,
            thresholds=Thresholds(max_error_rate=max_error_rate),
            explicit_confirmation=self.query_one(AuthorizationCheckbox).value,
            precheck_validated=self._precheck_validated,
            run_progress_notifier=_PanelProgressNotifier(
                self.query_one(ProgressPanel), run_progress
            ),
            notification_sink=self.query_one(NotificationBar),
            profile_id=self._selected_profile_id,
        )
        run_progress.stop()
        self.query_one("#stop-frame", Container).display = False

        if isinstance(outcome, Err):
            result_label.update(str(outcome.error))
            return
        result_label.update(f"Termine — {verdict_label(outcome.value)} (voir le detail).")
        self.app.push_screen(
            RunDetailsScreen(container=self._container, run_id=outcome.value.id)
        )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit le formulaire de lancement en appel a
#   controllers/load_controller.py::launch_ramp().
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Symetrique a screens/request_panel.py, seule differe la commande
#   application/ appelee (famille RAMP, montee progressive derivee par
#   domain/load/builders.py::build_ramp_steps()).
# Ce qu'il ne contient PAS :
# - Aucune saisie individuelle des etapes de rampe : entierement derivees
#   du niveau choisi par domain/load/presets.py::ramp_preset(), comme deja
#   documente cote application/commands/run_ramp_load.py.
# Points cles :
# - Duplication assumee avec request_panel.py/connection_panel.py plutot
#   qu'une base commune, meme raison que documentee dans
#   connection_panel.py.
# - Aucune regle de guard reimplementee : le bouton "Pre-check" (voir
#   Points cles) ne fait qu'exposer controllers/load_controller.py::
#   launch_precheck(), deja ecrit et deja utilise par le CLI
#   (`omega-stress run precheck`) — ce fichier n'invente aucune logique.
# - Push RunDetailsScreen sur Ok (2026-08-24) : meme mecanisme et meme
#   raison que documentee dans request_panel.py.
# - RunProgress start()/stop() : meme emplacement/raison que documente
#   dans request_panel.py.
# - Selecteur "profile" (2026-08-24) : meme mecanisme que
#   request_panel.py, filtre sur family == RAMP.
# - #duration/#max-error-rate en Select (2026-08-24) : meme mecanisme et
#   meme raison que documentee dans request_panel.py.
# - Bouton "Pre-check" (2026-08-24) : mirroir exact de request_panel.py
#   (meme raison, meme mecanisme — visible seulement si is_precheck_mandatory()
#   sur le niveau choisi, memorise self._precheck_validated, transmis a
#   launch_ramp() a la place du "precheck_validated=False" fige avant ce
#   correctif).
# - Bouton "Arreter" (2026-08-25) : mirroir exact de request_panel.py,
#   voir son INFO DEV pour le mecanisme complet (Worker.cancel() ->
#   asyncio.CancelledError absorbee par application/pipeline/executor.py
#   -> cloture normale AUTO_STOPPED).
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Test charge").
#---------------------------------------------------------------------->
