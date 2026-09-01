# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de lancement d'un Test requetes (debit)."""
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
"""Options de #duration au moment du compose() : Select(allow_blank=False)
leve EmptySelectError si construit avec une liste vide (voir INFO DEV) —
_set_duration_options() les recalcule de toute facon des que l'utilisateur
choisit un niveau."""
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
    """Niveaux proposes par ce profil de duree : jusqu'a free_max_level
    inclus, plus reinforced_level s'il existe (voir domain/load/
    duration_presets.py::DurationPreset) — jamais la liste complete."""
    ordered = list(IntensityLevel)
    allowed = ordered[: ordered.index(preset.free_max_level) + 1]
    if preset.reinforced_level is not None:
        allowed.append(preset.reinforced_level)
    return [(level.value, level) for level in allowed]


class _PanelProgressNotifier:
    """Adapte widgets/progress_panel.py au port RunProgressNotifier
    (methode notify(), appelee sur la meme boucle asyncio que le
    pipeline puisque le runner s'execute in-process, jamais dans un
    thread separe — aucune synchronisation supplementaire necessaire)."""

    def __init__(self, panel: ProgressPanel, progress: RunProgress) -> None:
        self._panel = panel
        self._progress = progress

    def notify(self, run_id: str, sample: IntervalSample) -> None:
        self._panel.update_sample(sample)
        self._progress.update_elapsed(sample.at_second)


class RequestPanelScreen(OmegaScreen):
    """Formulaire de lancement d'un Test requetes en mode manuel borne."""

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
            yield Static("TEST REQUETES", classes="omega-title")
            yield Select([], prompt="Profil fige (optionnel)", id="profile")
            yield TargetPicker(id="target-picker")
            yield Static("Criteres du test", classes="omega-subtitle")
            yield Select(_LEVEL_OPTIONS, prompt="Intensite", id="level", allow_blank=False)
            yield Select(
                _DURATION_MODE_OPTIONS, prompt="Mode duree", id="duration-mode",
                allow_blank=False,
            )
            yield Select(
                _DEFAULT_DURATION_OPTIONS, prompt="Duree (minutes)", id="duration",
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
            if p.frozen and p.family == TestFamily.REQUEST.value
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
        """Recalcule les durees proposees pour le niveau donne (seule
        source de verite : domain/load/policies.py::allowed_durations_minutes()).
        Si `keep_value` n'est plus valide pour ce niveau, retombe sur la
        premiere duree autorisee et le signale dans #result."""
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
        """Bascule entre mode manuel (#duration, niveaux complets) et mode
        profil D1-D6 (#duration-preset, niveaux filtres) — les deux Select
        de duree ne sont jamais visibles en meme temps."""
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
                family=TestFamily.REQUEST,
                target_value=preset.requests_per_minute / 60.0,
                unit="req/s",
                result=result,
            )
        )
        comparison.display = True

    def _apply_profile(self, profile: ProfileDTO) -> None:
        # Un profil fige ne porte aucune notion de profil de duree D1-D6
        # (concept exclusivement mode manuel) : force le mode manuel avant
        # de pre-remplir, sinon un niveau filtre par un profil de duree
        # choisi precedemment pourrait rejeter le niveau du profil.
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
        outcome = await load_controller.launch_request(
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
#   controllers/load_controller.py::launch_request().
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Aucune logique de guard/pipeline ici (deja dans application/pipeline/),
#   ce fichier assemble seulement les parametres et affiche le resultat.
# Ce qu'il ne contient PAS :
# - Aucune regle de guard reimplementee : le bouton "Pre-check" (voir
#   Points cles) ne fait qu'exposer controllers/load_controller.py::
#   launch_precheck(), deja ecrit et deja utilise par le CLI
#   (`omega-stress run precheck`) — ce fichier n'invente aucune logique.
# Points cles :
# - run_worker(..., exclusive=True) : lance le run dans un worker Textual
#   dedie, sans bloquer la boucle d'evenements de l'ecran ; exclusive=True
#   annule un lancement precedent si l'utilisateur clique deux fois avant
#   la fin du premier (protection simple contre le double-lancement).
# - Push RunDetailsScreen sur Ok (2026-08-24, remplace un resume texte
#   "verdict — metriques" reste dans "#result") : "#result" ne montre plus
#   qu'un rappel court ("Termine — <verdict>") pendant que
#   RunDetailsScreen (deja enrichi de sa propre chronologie ASCII, voir
#   son INFO DEV) s'affiche par-dessus avec le detail complet — avant ce
#   correctif, le seul detail visible immediatement apres un scan etait
#   cette unique ligne, l'utilisateur devait repasser par l'Historique
#   pour voir quoi que ce soit de plus (RunDTO.events/sample_count deja
#   enrichis en amont, mais jamais affiches nulle part directement apres
#   un lancement). Uniquement sur Ok : un Err ici est un rejet de guard
#   AVANT toute execution, aucun run n'existe encore a afficher.
# - result_label.update("Lancement en cours…") (2026-08-24) juste avant
#   la validation du formulaire : sans cela, le message d'un ECHEC
#   PRECEDENT (ex. "non autorise") restait affiche tel quel pendant toute
#   la duree d'un nouveau lancement reussi (jusqu'a plusieurs minutes),
#   laissant croire a l'utilisateur que ce nouveau lancement avait
#   lui-meme echoue alors qu'il etait simplement en cours — bug reel
#   rapporte le meme jour. Complete depuis par widgets/run_progress.py
#   (jauge + ETA), voir ci-dessous.
# - RunProgress (2026-08-24) : start() juste avant l'appel de lancement
#   (duration_minutes deja valide a ce point, converti en secondes),
#   stop() juste apres reception de l'outcome, quel que soit son type
#   (Err ou Ok) — la jauge doit disparaitre des que le run est termine,
#   pas seulement en cas de succes.
# - _resolve_target() privilegie la saisie manuelle sur la selection dans
#   la liste connue si les deux sont presentes : coherent avec
#   widgets/target_picker.py, ou la saisie manuelle est l'action la plus
#   recente de l'utilisateur.
# - Une cible non epinglee (id = valeur manuelle brute) exige la case
#   d'autorisation cochee : sinon application/pipeline/guards/
#   authorization_guard.py refuse, message relaye tel quel dans #result.
# - Selecteur "profile" (2026-08-24) : ne filtre QUE les profils figes de
#   famille REQUEST (un profil connexions/charge n'a pas de sens ici) —
#   _apply_profile() pre-remplit niveau/duree/seuil/cible et memorise
#   profile_id, transmis tel quel a launch_request(). Avant ce correctif,
#   AUCUN ecran ne transmettait jamais profile_id (toujours None), ce qui
#   empechait aussi "Rejouer" depuis l'Historique de fonctionner un jour
#   (replay_run() exige un run deja lie a un profil, domain/runs/
#   validators.py::can_be_replayed()) — un profil fige n'avait donc
#   litteralement aucun effet observable avant ce jour, malgre
#   to_load_plan()/replay_run() deja entierement ecrits et testes cote
#   domaine/application.
# - Remettre "profile" a vide (Select.BLANK) efface profile_id mais NE
#   REINITIALISE PAS les champs deja pre-remplis : l'utilisateur peut
#   partir d'un profil puis ajuster manuellement sans tout reperdre, le
#   lancement redevient alors un mode manuel borne ordinaire (profile_id
#   redevient None, la tracabilite du profil est perdue, mais les valeurs
#   restent).
# - #duration/#max-error-rate en Select (2026-08-24, remplace deux Input
#   libres + int()/float()/ValueError) : la duree n'est plus une saisie
#   libre mais calibree par domain/load/policies.py::
#   allowed_durations_minutes(level), SEULE source de verite (jamais gate
#   -> 1-5 min, gate optionnel -> 1/2/3 min, +4/5 min si pre-check
#   facultatif valide, gate obligatoire -> 1/2/3 min quel que soit le
#   pre-check — modele a 3 paliers depuis Phase 3, 2026-09-01, voir
#   policies.py) — jamais dupliquee ici. _set_duration_options() recalcule
#   les options a chaque changement de "level" (on_select_changed) ; si la
#   duree deja choisie devient invalide pour le nouveau niveau, retombe
#   sur la premiere option valide et le signale dans #result plutot que de
#   laisser une valeur fantome. Taux d'erreur : 11 options fixes (0.0 a
#   1.0 par pas de 0.1), pure commodite de saisie, aucune regle de domaine
#   a consommer pour ce champ.
# - Bouton "Pre-check" (2026-08-24) : visible si le niveau choisi le
#   permet, obligatoire ou non (domain/load/policies.py::
#   is_precheck_available(), bascule dans on_select_changed sur "level" —
#   avant Phase 3 (2026-09-01) c'etait is_precheck_mandatory(), qui
#   n'aurait jamais propose le bouton sur un niveau gate optionnel comme
#   Puissant/Agressif, empechant de debloquer leurs durees etendues) — masque
#   par defaut (#level demarre vide). AVANT le tout premier correctif
#   (2026-08-24), AUCUN ecran TUI n'appelait jamais
#   load_controller.launch_precheck() (deja ecrit, deja utilise par
#   `omega-stress run precheck` cote CLI) : un niveau gate obligatoire
#   echouait donc systematiquement au lancement (precheck_guard.py,
#   toujours precheck_validated=False), sans aucun moyen de le satisfaire
#   depuis le TUI. self._precheck_validated est un simple booleen memoire
#   d'ecran, jamais invalide automatiquement si la cible change ensuite
#   (coherent avec application/pipeline/guards/precheck_guard.py, qui ne
#   verifie lui non plus jamais QUELLE cible a ete pre-checkee — meme
#   niveau de confiance des deux cotes).
# - _run_precheck() reutilise run_progress/ProgressPanel/NotificationBar
#   deja presents sur l'ecran (pas de composants dedies) : un Pre-check
#   est un vrai run cadence a 1 minute (run_precheck.py), la meme
#   indication de progression a du sens que pour un lancement normal.
# - Bouton "Arreter" (2026-08-25) : avant ce correctif, aucun moyen
#   d'interrompre un test/pre-check en cours autrement que quitter
#   l'application (bug reel rapporte). self._active_worker memorise le
#   Worker Textual retourne par run_worker() (lancement ou pre-check,
#   jamais les deux en meme temps grace a exclusive=True), "Arreter"
#   appelle Worker.cancel() dessus. La cancellation asyncio qui en
#   resulte est absorbee et transformee en cloture normale du run cote
#   application/pipeline/executor.py (voir son propre INFO DEV,
#   "Arret manuel") : _launch()/_run_precheck() reprennent donc APRES
#   l'await comme pour n'importe quelle fin de run (run_progress.stop(),
#   masquage de "#stop", RunDetailsScreen pousse avec un verdict
#   AUTO_STOPPED), sans bloc try/except supplementaire ici.
# - Mode duree "#duration-mode" (2026-09-01, D1-D6, coexiste avec le mode
#   manuel existant) : #duration (manuel, entiers) et #duration-preset
#   (profil, DurationPresetId) ne sont JAMAIS visibles en meme temps
#   (.display bascule sur "#duration-mode") — deux Select distincts
#   plutot qu'un seul reutilise pour deux types de valeur, pour ne
#   jamais melanger int et DurationPresetId dans le meme widget.
#   _apply_duration_preset() filtre "#level" aux seuls niveaux du profil
#   (free_max_level + reinforced_level, jamais la liste complete) et
#   retombe sur le premier niveau autorise si le niveau deja choisi
#   devient invalide pour le nouveau profil — meme patron que
#   _set_duration_options() en mode manuel. "#confirmation-frame"
#   (Input texte libre) n'apparait que si le niveau choisi EST
#   exactement le reinforced_level du profil courant ; la coquille
#   editee est reinitialisee des qu'elle redevient inutile (evite qu'un
#   texte tape pour un niveau precedent survive silencieusement a un
#   changement de niveau/profil). "#precheck-frame" (is_precheck_
#   available) reste gouverne uniquement par le NIVEAU, jamais par le
#   mode duree : un niveau gate obligatoire (Violent/Maximum) exige
#   toujours precheck_validated=True, meme en mode profil — les deux
#   gardes (precheck de niveau, confirmation renforcee de profil) sont
#   indépendantes et peuvent s'appliquer simultanement.
# - "#safety-mode"/"#calibration-comparison" (2026-09-01, bug reel
#   rapporte avec captures d'ecran : le garde-fou CPU generateur
#   arretait des tests sains) : SafetyModeCheckbox coche par defaut,
#   bascule UNIQUEMENT LoadPlan.safety_mode (jamais les guards qui
#   protegent la CIBLE, toujours actifs). "#calibration-comparison"
#   reste masque tant que la case est cochee ; des qu'elle est decochee
#   (ou que le niveau change alors qu'elle l'est deja), affiche la
#   comparaison entre ce que ce niveau vise et l'enveloppe du dernier
#   calibrage exploitable pour CETTE machine (presenters/calibration_
#   presenter.py::envelope_comparison_message()) — purement informatif,
#   jamais un blocage : demande explicite de l'utilisateur, relier le
#   calibrage (mesure) au mode securite (execution) sans les coupler
#   automatiquement.
# Comment il sera utilise :
# - interfaces/tui/screens/home.py (bouton "Test requetes").
#---------------------------------------------------------------------->
