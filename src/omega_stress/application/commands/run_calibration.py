# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : lancer un calibrage complet (mesure de la capacite reelle
de la machine, progression par paliers, persistance de l'enveloppe
sure)."""
from __future__ import annotations

from collections.abc import Callable

from omega_stress.application.pipeline.hooks.notification_hook import NotificationSink
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.calibration.exceptions import CalibrationPreconditionError
from omega_stress.domain.calibration.models import (
    CalibrationFingerprint,
    CalibrationResult,
    CalibrationStageResult,
)
from omega_stress.domain.calibration.policies import (
    CALIBRATION_STAGES,
    CALIBRATION_STOP_RPS_ACHIEVED_RATIO_MAX,
)
from omega_stress.domain.calibration.validators import (
    compute_envelope,
    evaluate_preconditions,
    evaluate_stage_outcome,
)
from omega_stress.ports.calibration_local_server import CalibrationServer
from omega_stress.ports.calibration_preconditions_probe import CalibrationPreconditionsProbe
from omega_stress.ports.calibration_repository import CalibrationRepository
from omega_stress.ports.calibration_stage_progress_notifier import (
    CalibrationStageProgressNotifier,
)
from omega_stress.ports.calibration_stage_runner import CalibrationStageRunner
from omega_stress.shared.typing import Clock


async def run_calibration(
    *,
    compute_fingerprint: Callable[[], CalibrationFingerprint],
    preconditions_probe: CalibrationPreconditionsProbe,
    server_factory: Callable[[], CalibrationServer],
    stage_runner_factory: Callable[[], CalibrationStageRunner],
    calibration_repository: CalibrationRepository,
    now: Clock,
    notification_sink: NotificationSink,
    stage_progress_notifier: CalibrationStageProgressNotifier,
    another_calibration_or_run_active: bool = False,
) -> Result[CalibrationResult, CalibrationPreconditionError]:
    """Orchestre un calibrage complet : preconditions -> serveur local ->
    progression par paliers (arret ou saut des paliers conditionnels
    selon les verdicts) -> enveloppe -> persistance.

    another_calibration_or_run_active : fourni par l'appelant (etat en
    memoire du processus TUI/CLI, jamais mesure ici) — voir domain/
    calibration/validators.py::evaluate_preconditions()."""
    fingerprint = compute_fingerprint()
    snapshot = await preconditions_probe.read()
    precondition_check = evaluate_preconditions(
        cpu_global_percent=snapshot.cpu_global_percent,
        memory_available_percent=snapshot.memory_available_percent,
        swap_active_or_growing=snapshot.swap_active_or_growing,
        load_average_1min=snapshot.load_average_1min,
        logical_cpu_count=snapshot.logical_cpu_count,
        another_calibration_or_run_active=another_calibration_or_run_active,
    )
    if isinstance(precondition_check, Err):
        return precondition_check

    started_at = now()
    stage_results: list[CalibrationStageResult] = []
    healthy_results: list[CalibrationStageResult] = []
    first_degraded_stage_id: str | None = None
    overall_stop_reason: str | None = None
    previous_stage_healthy = True
    previous_stage_rps_below_ratio = False

    with server_factory() as server:
        async with stage_runner_factory() as runner:
            for stage in CALIBRATION_STAGES:
                if stage.conditional and not previous_stage_healthy:
                    break

                measurement = await runner.run_stage(
                    stage,
                    base_url=server.base_url,
                    stage_progress_notifier=stage_progress_notifier,
                )
                stage_result = evaluate_stage_outcome(
                    stage,
                    rps_achieved=measurement.rps_achieved,
                    error_rate=measurement.error_rate,
                    system_samples=measurement.system_samples,
                    consecutive_timeouts=measurement.consecutive_timeouts,
                    previous_stage_rps_below_ratio=previous_stage_rps_below_ratio,
                )
                stage_results.append(stage_result)
                notification_sink(
                    f"Palier {stage.name} : "
                    f"{'sain' if stage_result.is_healthy else 'degrade'}"
                    f"{f' — {stage_result.stop_reason}' if stage_result.stop_reason else ''}"
                )

                if stage_result.is_healthy:
                    healthy_results.append(stage_result)
                elif first_degraded_stage_id is None:
                    first_degraded_stage_id = stage_result.stage_id

                previous_stage_healthy = stage_result.is_healthy
                rps_ratio = (
                    stage_result.rps_achieved / stage.rps_target if stage.rps_target > 0 else 1.0
                )
                previous_stage_rps_below_ratio = rps_ratio < CALIBRATION_STOP_RPS_ACHIEVED_RATIO_MAX

                if stage_result.stop_reason is not None:
                    overall_stop_reason = stage_result.stop_reason
                    break

    finished_at = now()
    envelope = compute_envelope(healthy_results, first_degraded_stage_id=first_degraded_stage_id)
    result = CalibrationResult(
        fingerprint=fingerprint,
        started_at=started_at,
        duration_seconds=(finished_at - started_at).total_seconds(),
        stages=tuple(stage_results),
        envelope=envelope,
        overall_stop_reason=overall_stop_reason,
    )
    calibration_repository.save(result)
    return Ok(result)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'orchestration unique du calibrage : preconditions, serveur
#   local, progression par paliers, enveloppe, persistance — meme role
#   que application/pipeline/executor.py pour un run reel, mais un flux
#   plus simple (pas de guards separes, l'evaluation est faite palier par
#   palier de facon sequentielle et bloquante, jamais un flux continu
#   d'IntervalSample consomme par un guard externe).
# Pourquoi dans application/commands/ (charte) :
# - Orchestre des ports (jamais d'infrastructure/ importee directement,
#   Dependency Rule) et de la logique pure de domain/calibration/ —
#   meme structure que les commands run_*_load.py existants.
# Ce qu'il ne contient PAS :
# - Aucune construction d'infrastructure concrete : compute_fingerprint/
#   server_factory/stage_runner_factory sont des CALLABLES injectes
#   (meme patron que shared/typing.py::IdFactory/Clock), jamais un import
#   direct de infrastructure/calibration/ — app/dependency_container.py
#   passe les classes concretes elles-memes comme factories (instancier
#   une classe = l'appeler avec zero argument, forme exacte attendue par
#   Callable[[], ...]).
# - Aucun calcul de seuil (voir domain/calibration/policies.py et
#   validators.py, cette fonction ne fait qu'orchestrer leurs appels dans
#   le bon ordre).
# Points cles :
# - Paliers conditionnels (calib_5/calib_6, stage.conditional=True) :
#   sautes (break, jamais juste "ignores" — la boucle s'arrete net) des
#   que le palier PRECEDENT n'est pas sain, coherent avec le document
#   ("les paliers 5 et 6 ne sont executes que si le palier precedent est
#   sain") — previous_stage_healthy demarre a True (idle_baseline n'est
#   jamais conditionnel, cette valeur initiale n'est donc jamais lue
#   avant la premiere vraie evaluation).
# - previous_stage_rps_below_ratio : calcule ICI (pas dans le domaine)
#   car c'est un etat de PROGRESSION a travers plusieurs paliers, pas une
#   propriete d'un seul palier isole — domain/calibration/validators.py::
#   evaluate_stage_outcome() reste une fonction pure sans memoire propre.
# - notification_sink appele apres CHAQUE palier (pas seulement a la fin) :
#   un calibrage dure potentiellement plusieurs minutes (7 paliers, 5 a
#   20s chacun), l'utilisateur doit voir la progression en direct — meme
#   raison que RunProgress/NotificationBar pour un run reel.
# - stage_progress_notifier (2026-09-02, bug reel rapporte : "le
#   calibrage semble geler" sur un palier plus lent que prevu, voir
#   ports/calibration_stage_progress_notifier.py pour le diagnostic
#   complet) : transmis TEL QUEL a runner.run_stage(), jamais interprete
#   ici — ce fichier ne fait qu'acheminer ce port comme il achemine deja
#   notification_sink, la granularite fine (seconde par seconde PENDANT
#   un palier) reste un detail d'infrastructure/calibration/
#   stage_runner.py.
# - now: Clock, pas datetime (meme raison que application/pipeline/
#   executor.py/abort.py) : appelee fraichement au debut ET a la fin,
#   jamais une valeur figee reutilisee pour les deux (duration_seconds
#   refleterait sinon toujours 0).
# - calibration_repository.save() est appele MEME si overall_stop_reason
#   n'est pas None (calibrage arrete en cours de route) : un calibrage
#   degrade/interrompu reste un resultat persistable et consultable
#   (voir domain/calibration/models.py::CalibrationResult, meme principe
#   que "envelope: None reste un resultat valide").
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/calibration_screen.py (bouton "Lancer le
#   calibrage"), interfaces/cli/commands/calibrate_command.py.
#---------------------------------------------------------------------->
