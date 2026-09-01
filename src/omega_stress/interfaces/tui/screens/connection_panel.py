# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de lancement d'un Test connexions (simultaneite)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Footer, Header, Input, OptionList, Select, Static
from textual.worker import Worker

from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.core.enums import DurationPresetId, IntensityLevel, TestFamily
from omega_stress.core.results import Err
from omega_stress.domain.load.duration_presets import DurationPreset, duration_preset
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.load.policies import (
    SAFETY_MODE_DESCRIPTION,
    allowed_durations_minutes,
    is_precheck_available,
)
from omega_stress.domain.load.presets import fixed_rate_preset
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.interfaces.tui.controllers import (
    calibration_controller,
    load_controller,
    profile_controller,
)
from omega_stress.interfaces.tui.presenters.calibration_presenter import (
    envelope_comparison_message,
)
from omega_stress.interfaces.tui.presenters.run_presenter import verdict_label
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.run_details import RunDetailsScreen
from omega_stress.interfaces.tui.widgets.authorization_checkbox import AuthorizationCheckbox
from omega_stress.interfaces.tui.widgets.notification_bar import NotificationBar
from omega_stress.interfaces.tui.widgets.progress_panel import ProgressPanel
from omega_stress.interfaces.tui.widgets.run_progress import RunProgress
from omega_stress.interfaces.tui.widgets.safety_mode_checkbox import SafetyModeCheckbox
from omega_stress.interfaces.tui.widgets.target_picker import TargetPicker

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer

_LEVEL_OPTIONS = [(level.value, level) for level in IntensityLevel]
_MAX_ERROR_RATE_OPTIONS = [(f"{v / 10:.1f}", v / 10) for v in range(11)]
_DEFAULT_DURATION_OPTIONS = [
    (f"{m} min", m) for m in allowed_durations_minutes(IntensityLevel.BAS)
]
"""Voir screens/request_panel.py, meme raison (EmptySelectError sinon)."""
_DURATION_MODE_OPTIONS = [("Manuel (1-5 min)", "manual"), ("Profil D1-D6", "preset")]
_DURATION_PRESET_OPTIONS = [
    (
        f"{preset_id.value.upper()} {duration_preset(preset_id).name} "
        f"({duration_preset(preset_id).total_minutes} min)",
        preset_id,
    )
    for preset_id in DurationPresetId
]


def _level_options_for_preset(preset: DurationPreset) -> list[tuple[str, IntensityLevel]]:
    """Voir screens/request_panel.py, meme logique a l'identique."""
    ordered = list(IntensityLevel)
    allowed = ordered[: ordered.index(preset.free_max_level) + 1]
    if preset.reinforced_level is not None:
        allowed.append(preset.reinforced_level)
    return [(level.value, level) for level in allowed]


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


class ConnectionPanelScreen(OmegaScreen):
    """Formulaire de lancement d'un Test connexions en mode manuel borne."""

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
            yield Static("TEST CONNEXIONS", classes="omega-title")
            yield Select([], prompt="Profil fige (optionnel)", id="profile")
            yield TargetPicker(id="target-picker")
            yield Static("Criteres du test", classes="omega-subtitle")
            yield Select(_LEVEL_OPTIONS, prompt="Intensite", id="level", allow_blank=False)
            yield Select(
                _DURATION_MODE_OPTIONS, prompt="Mode duree", id="duration-mode",
                allow_blank=False,
            )
            yield Select(
                _DEFAULT_DURATION_OPTIONS,
                prompt="Duree (minutes)",
                id="duration",
                allow_blank=False,
            )
            yield Select(
                _DURATION_PRESET_OPTIONS, prompt="Profil de duree", id="duration-preset",
                allow_blank=False,
            )
            with Container(id="confirmation-frame", classes="omega-btn-frame"):
                yield Static("Confirmation renforcee requise pour ce niveau :")
                yield Input(placeholder="Texte de confirmation exact", id="confirmation-text")
            yield Select(
                _MAX_ERROR_RATE_OPTIONS,
                prompt="Taux d'erreur maximal",
                id="max-error-rate",
                allow_blank=False,
            )
            yield AuthorizationCheckbox(id="authorization")
            yield Static(SAFETY_MODE_DESCRIPTION, classes="omega-subtitle")
            yield SafetyModeCheckbox(id="safety-mode")
            yield Static("", id="calibration-comparison")
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
            if p.frozen and p.family == TestFamily.CONNECTION.value
        ]
        self.query_one("#profile", Select).set_options((p.name, p) for p in frozen_profiles)
        self._set_duration_options(IntensityLevel.BAS)
        self.query_one("#duration-mode", Select).value = "manual"
        self.query_one("#duration-preset", Select).display = False
        self.query_one("#confirmation-frame", Container).display = False
        self.query_one("#precheck-frame", Container).display = False
        self.query_one("#stop-frame", Container).display = False
        self.query_one("#calibration-comparison", Static).display = False

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

    def _is_preset_mode(self) -> bool:
        return self.query_one("#duration-mode", Select).value == "preset"

    def _apply_duration_mode(self, mode: object) -> None:
        """Voir screens/request_panel.py, meme logique a l'identique."""
        is_preset = mode == "preset"
        self.query_one("#duration", Select).display = not is_preset
        self.query_one("#duration-preset", Select).display = is_preset
        if is_preset:
            preset_value = self.query_one("#duration-preset", Select).value
            preset_id = (
                preset_value if isinstance(preset_value, DurationPresetId) else DurationPresetId.D1
            )
            self.query_one("#duration-preset", Select).value = preset_id
            self._apply_duration_preset(preset_id)
        else:
            self.query_one("#confirmation-frame", Container).display = False
            level_select = self.query_one("#level", Select)
            level_select.set_options(_LEVEL_OPTIONS)
            level = level_select.value
            if isinstance(level, IntensityLevel):
                self._set_duration_options(level)
                self.query_one("#precheck-frame", Container).display = is_precheck_available(level)

    def _apply_duration_preset(self, preset_id: DurationPresetId) -> None:
        preset = duration_preset(preset_id)
        level_select = self.query_one("#level", Select)
        options = _level_options_for_preset(preset)
        allowed_levels = [level for _label, level in options]
        current_level = level_select.value
        level_select.set_options(options)
        level_select.value = (
            current_level if current_level in allowed_levels else allowed_levels[0]
        )
        self.query_one("#precheck-frame", Container).display = is_precheck_available(
            level_select.value
        )
        self._refresh_confirmation_visibility(level_select.value)

    def _refresh_confirmation_visibility(self, level: IntensityLevel) -> None:
        preset_value = self.query_one("#duration-preset", Select).value
        preset = (
            duration_preset(preset_value) if isinstance(preset_value, DurationPresetId) else None
        )
        needs_confirmation = preset is not None and level is preset.reinforced_level
        self.query_one("#confirmation-frame", Container).display = needs_confirmation
        if not needs_confirmation:
            self.query_one("#confirmation-text", Input).value = ""

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "duration-mode":
            self._apply_duration_mode(event.value)
            return
        if event.select.id == "duration-preset" and isinstance(event.value, DurationPresetId):
            self._apply_duration_preset(event.value)
            return
        if event.select.id == "level" and isinstance(event.value, IntensityLevel):
            self.query_one("#precheck-frame", Container).display = is_precheck_available(
                event.value
            )
            if self._is_preset_mode():
                self._refresh_confirmation_visibility(event.value)
            else:
                current_duration = self.query_one("#duration", Select).value
                self._set_duration_options(
                    event.value,
                    keep_value=current_duration if isinstance(current_duration, int) else None,
                )
            self._refresh_calibration_comparison()
            return
        if event.select.id != "profile":
            return
        profile = event.value
        if not isinstance(profile, ProfileDTO):
            self._selected_profile_id = None
            return
        self._apply_profile(profile)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "safety-mode":
            self._refresh_calibration_comparison()

    def _refresh_calibration_comparison(self) -> None:
        comparison = self.query_one("#calibration-comparison", Static)
        if self.query_one(SafetyModeCheckbox).value:
            comparison.display = False
            return
        level = self.query_one("#level", Select).value
        if not isinstance(level, IntensityLevel):
            comparison.display = False
            return
        preset = fixed_rate_preset(level)
        result = calibration_controller.load_last_calibration(self._container)
        comparison.update(
            envelope_comparison_message(
                family=TestFamily.CONNECTION,
                target_value=float(preset.concurrent_connections),
                unit="connexions",
                result=result,
            )
        )
        comparison.display = True

    def _apply_profile(self, profile: ProfileDTO) -> None:
        # Voir screens/request_panel.py, meme raison (aucun profil de
        # duree D1-D6 sur un profil fige).
        self.query_one("#duration-mode", Select).value = "manual"
        self._apply_duration_mode("manual")
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

        max_error_rate = self.query_one("#max-error-rate", Select).value
        if not isinstance(max_error_rate, float):
            result_label.update("Choisissez un taux d'erreur.")
            return

        if self._is_preset_mode():
            preset_value = self.query_one("#duration-preset", Select).value
            if not isinstance(preset_value, DurationPresetId):
                result_label.update("Choisissez un profil de duree.")
                return
            duration_minutes = duration_preset(preset_value).total_minutes
            duration_preset_id: DurationPresetId | None = preset_value
            confirmation_text = self.query_one("#confirmation-text", Input).value or None
        else:
            manual_duration = self.query_one("#duration", Select).value
            if not isinstance(manual_duration, int):
                result_label.update("Choisissez une duree.")
                return
            duration_minutes = manual_duration
            duration_preset_id = None
            confirmation_text = None

        run_progress = self.query_one(RunProgress)
        run_progress.start(total_seconds=duration_minutes * 60)
        self.query_one("#stop-frame", Container).display = True
        outcome = await load_controller.launch_connection(
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
            duration_preset_id=duration_preset_id,
            reinforced_confirmation_text=confirmation_text,
            safety_mode=self.query_one(SafetyModeCheckbox).value,
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
#   controllers/load_controller.py::launch_connection().
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Symetrique a screens/request_panel.py, seule differe la commande
#   application/ appelee (famille CONNECTION plutot que REQUEST).
# Ce qu'il ne contient PAS :
# - Aucune notion de debit demande dans le formulaire : un Test connexions
#   n'a pas de champ requetes/minute (voir domain/load/presets.py, meme
#   absence deja documentee cote application/commands/
#   run_connection_load.py).
# - Aucune regle de guard reimplementee : le bouton "Pre-check" (voir
#   Points cles) ne fait qu'exposer controllers/load_controller.py::
#   launch_precheck(), deja ecrit et deja utilise par le CLI
#   (`omega-stress run precheck`) — ce fichier n'invente aucune logique.
# Points cles :
# - Duplication assumee avec request_panel.py/ramp_panel.py plutot qu'une
#   base commune : ARCHITECTURE.md §2 liste ces trois ecrans comme fichiers
#   independants (comme les trois commands run_*_load.py qu'ils appellent),
#   pas un run_panel.py generique.
# - Push RunDetailsScreen sur Ok (2026-08-24) : meme mecanisme et meme
#   raison que documentee dans request_panel.py.
# - RunProgress start()/stop() : meme emplacement/raison que documente
#   dans request_panel.py.
# - Selecteur "profile" (2026-08-24) : meme mecanisme que
#   request_panel.py, filtre sur family == CONNECTION.
# - #duration/#max-error-rate en Select (2026-08-24) : meme mecanisme et
#   meme raison que documentee dans request_panel.py.
# - Bouton "Pre-check" (2026-08-24) : mirroir exact de request_panel.py
#   (meme raison, meme mecanisme — visible seulement si is_precheck_available()
#   sur le niveau choisi (2026-09-01, gate optionnel OU obligatoire — avant
#   Phase 3 c'etait is_precheck_mandatory(), qui n'aurait jamais propose le
#   bouton sur un niveau gate optionnel comme Puissant/Agressif), memorise
#   self._precheck_validated, transmis a launch_connection() a la place du
#   "precheck_validated=False" fige avant ce correctif).
# - Bouton "Arreter" (2026-08-25) : mirroir exact de request_panel.py,
#   voir son INFO DEV pour le mecanisme complet (Worker.cancel() ->
#   asyncio.CancelledError absorbee par application/pipeline/executor.py
#   -> cloture normale AUTO_STOPPED).
# - Mode duree "#duration-mode" (2026-09-01, D1-D6) : mirroir exact de
#   request_panel.py (voir son INFO DEV pour le detail complet) — seule
#   famille hors Test charge ou le mode profil peuple aussi ramp_steps
#   (construit dans application/commands/run_connection_load.py, pas ici :
#   ce fichier transmet seulement level/duration_minutes/
#   duration_preset_id, jamais les etapes de rampe elles-memes).
# - "#safety-mode"/"#calibration-comparison" (2026-09-01) : mirroir exact
#   de request_panel.py (voir son INFO DEV pour le detail complet) —
#   seule difference, la comparaison ici porte sur les CONNEXIONS
#   simultanees visees par le niveau (FixedRatePreset.concurrent_
#   connections) plutot que sur un debit, comparees a envelope.
#   connections_safe (pas envelope.rps_safe).
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Test connexions").
#---------------------------------------------------------------------->
