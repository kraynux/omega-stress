# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de calibrage local persistant : consultation du dernier resultat
connu, declenchement d'un nouveau calibrage avec progression en direct."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static
from textual.worker import Worker

from omega_stress.core.results import Err
from omega_stress.domain.calibration.policies import CALIBRATION_STAGES
from omega_stress.interfaces.tui.controllers import calibration_controller
from omega_stress.interfaces.tui.presenters.calibration_presenter import (
    age_reminder,
    envelope_summary,
    stage_lines,
)
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.widgets.notification_bar import NotificationBar
from omega_stress.interfaces.tui.widgets.run_progress import RunProgress
from omega_stress.shared.clock import utc_now

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer

_TOTAL_CALIBRATION_SECONDS: float = float(
    sum(stage.window_seconds for stage in CALIBRATION_STAGES)
)

def _compute_stage_offsets() -> dict[str, int]:
    """Secondes cumulees de tous les paliers PRECEDENTS (pas celui-ci)
    dans l'ordre fixe de CALIBRATION_STAGES — reutilise par
    _StageProgressNotifier pour convertir une progression LOCALE a un
    palier en position GLOBALE sur RunProgress, sans jamais avoir besoin
    d'un compteur mutable partage entre appels."""
    offsets: dict[str, int] = {}
    cumulative = 0
    for stage in CALIBRATION_STAGES:
        offsets[stage.id] = cumulative
        cumulative += stage.window_seconds
    return offsets


_STAGE_OFFSETS: dict[str, int] = _compute_stage_offsets()


class _StageProgressNotifier:
    """Adapte widgets/run_progress.py au port CalibrationStageProgressNotifier
    (voir son propre INFO DEV) — publie une progression PENDANT un palier,
    pas seulement entre deux paliers (bug reel corrige le 2026-09-02 :
    "le calibrage semble geler" sur un palier plus lent que prevu)."""

    def __init__(self, progress: RunProgress) -> None:
        self._progress = progress

    def notify(self, stage_id: str, elapsed_seconds: int, window_seconds: int) -> None:
        self._progress.update_elapsed(_STAGE_OFFSETS[stage_id] + elapsed_seconds)


class CalibrationScreen(OmegaScreen):
    """Consultation/declenchement du calibrage local (mecanisme de mesure
    seul — aucun plafonnement des valeurs de lancement reel, voir
    INFO DEV plus bas)."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._active_worker: Worker[None] | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("CALIBRAGE", classes="omega-title")
            yield Static(
                "Mesure la capacite reelle de CETTE machine (pas la cible testee) via "
                "un serveur de boucle locale, par paliers de charge croissante. Le "
                "resultat n'est pas encore applique aux tests reels : consultation "
                "seule pour l'instant.",
                classes="omega-subtitle",
            )
            yield Static("", id="last-result")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Lancer le calibrage", id="launch", variant="primary")
                with Container(id="stop-frame", classes="omega-btn-frame"):
                    yield Button("Arreter", id="stop", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
            yield RunProgress(id="run-progress")
            yield NotificationBar(id="notifications")
            yield Static("", id="stages")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#stop-frame", Container).display = False
        self._refresh_last_result()

    def _refresh_last_result(self) -> None:
        result = calibration_controller.load_last_calibration(self._container)
        label = self.query_one("#last-result", Static)
        stages = self.query_one("#stages", Static)
        if result is None:
            label.update("Aucun calibrage connu pour cette machine.")
            stages.update("")
            return
        label.update(f"{envelope_summary(result)}\n{age_reminder(result, now=utc_now())}")
        stages.update("\n".join(stage_lines(result)))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "launch":
            self._active_worker = self.run_worker(self._launch(), exclusive=True)
        elif event.button.id == "stop" and self._active_worker is not None:
            self._active_worker.cancel()

    async def _launch(self) -> None:
        notifications = self.query_one(NotificationBar)
        notifications.clear_message()
        run_progress = self.query_one(RunProgress)
        run_progress.start(total_seconds=_TOTAL_CALIBRATION_SECONDS)
        self.query_one("#stop-frame", Container).display = True
        self.query_one("#launch", Button).disabled = True

        try:
            outcome = await calibration_controller.launch_calibration(
                container=self._container,
                notification_sink=notifications,
                stage_progress_notifier=_StageProgressNotifier(run_progress),
            )
        finally:
            run_progress.stop()
            self.query_one("#stop-frame", Container).display = False
            self.query_one("#launch", Button).disabled = False

        if isinstance(outcome, Err):
            notifications(f"Calibrage refuse : {outcome.error}")
            return
        self._refresh_last_result()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Formulaire de declenchement + consultation du calibrage local
#   (mesure de la capacite reelle de la machine hote, jamais de la cible
#   testee) — voir domain/calibration/, application/commands/
#   run_calibration.py, controllers/calibration_controller.py.
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Aucune logique d'evaluation/enveloppe ici (deja dans domain/
#   calibration/validators.py) : cet ecran assemble seulement les appels
#   au controller et affiche le resultat.
# Ce qu'il ne contient PAS :
# - Aucun plafonnement des valeurs appliquees a un lancement reel : ce
#   chantier est explicitement borne au MECANISME DE MESURE seul (choix
#   utilisateur tranche via AskUserQuestion, 2026-09-01) — la formule
#   min(niveau, safe) sur les 3 ecrans de lancement (request_panel.py,
#   connection_panel.py, ramp_panel.py) et validate_plan() reste un
#   chantier suivant delibere, non commence ici.
# Points cles :
# - RunProgress/NotificationBar reutilises tels quels (widgets deja
#   existants, memes que les 3 ecrans de lancement) : un calibrage est
#   d'esprit un run comme un autre du point de vue de la presentation
#   (progression, notifications), aucun widget dedie necessaire.
# - _StageProgressNotifier (2026-09-02, remplace un premier _sink() qui
#   n'avancait RunProgress qu'a la fin de CHAQUE PALIER ENTIER — bug reel
#   rapporte avec capture d'ecran : "le calibrage semble geler... la
#   jauge n'avance plus", alors qu'un palier plus lent que prevu (meme
#   limite de capacite locale que Test connexions Agressif) tournait
#   simplement plusieurs dizaines de secondes SANS PRODUIRE le moindre
#   signal d'avancement avant sa toute fin, indiscernable d'un vrai gel).
#   Consomme desormais ports/calibration_stage_progress_notifier.py,
#   appele CHAQUE SECONDE ecoulee PENDANT un palier (voir infrastructure/
#   calibration/stage_runner.py) — _STAGE_OFFSETS convertit une
#   progression LOCALE au palier courant en position GLOBALE sur
#   RunProgress (deja utilise pour la duree TOTALE via
#   _TOTAL_CALIBRATION_SECONDS), sans etat mutable partage entre appels.
#   notification_sink (messages texte "Palier X : sain/degrade") reste
#   separe et toujours appele UNE FOIS PAR PALIER TERMINE seulement (voir
#   application/commands/run_calibration.py) — NotificationBar est
#   directement passee comme notification_sink (deja Callable[[str],
#   None] via son __call__, aucun wrapper necessaire).
# - try/finally autour de l'attente de launch_calibration() (2026-09-01) :
#   DIFFERENCE DELIBEREE avec les 3 ecrans de lancement reels. La-bas, une
#   Worker.cancel() (bouton "Arreter") remonte une asyncio.CancelledError
#   ABSORBEE par application/pipeline/executor.py, qui la transforme en
#   verdict AUTO_STOPPED normal — _launch()/_run_precheck() y reprennent
#   donc naturellement APRES l'await. run_calibration() n'a PAS cette
#   absorption (flux plus simple, pas de pipeline/guards separes, voir son
#   propre INFO DEV) : une CancelledError s'y propage telle quelle, sans
#   jamais atteindre calibration_repository.save() — un calibrage
#   interrompu manuellement N'EST DONC PAS PERSISTE (contrairement a un
#   run reel arrete manuellement, qui produit un LoadRun AUTO_STOPPED
#   consultable). Le try/finally garantit seulement que l'ECRAN se
#   reinitialise proprement (jauge masquee, bouton "Lancer" reactive) meme
#   dans ce cas, jamais qu'un resultat partiel soit sauvegarde — limitation
#   assumee, pas un bug : voir plan, chantier calibrage, "Angles morts".
# Comment il sera utilise :
# - screens/home.py (bouton "Calibrage").
#---------------------------------------------------------------------->
