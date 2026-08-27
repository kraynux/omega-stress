# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Etape 5/5 du pipeline : execution d'un plan valide, de bout en bout."""
from __future__ import annotations

import asyncio
from datetime import datetime

from omega_stress.application.exceptions import RunnerFailureError, UseCaseExecutionError
from omega_stress.application.pipeline.abort import abort_run
from omega_stress.application.pipeline.degraded_mode import is_local_bottleneck
from omega_stress.application.pipeline.guards.threshold_guard import check_threshold
from omega_stress.application.pipeline.hooks.audit_hook import (
    AuditSink,
    emit_run_finished,
    emit_run_started,
)
from omega_stress.application.pipeline.hooks.metrics_hook import publish_sample
from omega_stress.application.pipeline.hooks.notification_hook import (
    NotificationSink,
    notify_auto_stop,
    notify_local_bottleneck,
)
from omega_stress.core.enums import RunVerdict
from omega_stress.core.results import Err
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.runs.models import IntervalSample, LoadRun, RunEvent
from omega_stress.domain.runs.service import aggregate_samples, finish
from omega_stress.ports.load_runner import LoadRunner
from omega_stress.ports.run_progress_notifier import RunProgressNotifier
from omega_stress.shared.typing import Clock


async def execute(
    plan: LoadPlan,
    *,
    run: LoadRun,
    target_url: str,
    requested_rate_per_minute: int | None,
    load_runner: LoadRunner,
    run_progress_notifier: RunProgressNotifier,
    audit_sink: AuditSink,
    notification_sink: NotificationSink,
    now: Clock,
) -> LoadRun:
    """Execute un plan deja valide (application/pipeline/planner.py) de
    bout en bout : consomme le flux de mesures, publie la progression,
    evalue les seuils en continu, et cloture le run — normalement, par
    arret automatique, ou en echec technique."""
    emit_run_started(run, sink=audit_sink)

    collected: list[IntervalSample] = []
    bottleneck_notified = False

    try:
        async for sample in load_runner.run(plan, target_url=target_url):
            collected.append(sample)
            publish_sample(run.id, sample, notifier=run_progress_notifier)

            if not bottleneck_notified and is_local_bottleneck(
                sample, requested_rate_per_minute=requested_rate_per_minute
            ):
                notify_local_bottleneck(sink=notification_sink)
                bottleneck_notified = True

            threshold_result = check_threshold(sample, thresholds=plan.thresholds)
            if isinstance(threshold_result, Err):
                aborted = abort_run(
                    run, samples=tuple(collected), reason=threshold_result.error, now=now
                )
                notify_auto_stop(str(threshold_result.error), sink=notification_sink)
                emit_run_finished(aborted, sink=audit_sink)
                return aborted
    except RunnerFailureError as exc:
        failed_at = now()
        return _finish_with_verdict(
            run,
            samples=tuple(collected),
            verdict=RunVerdict.FAILED,
            requested_rate_per_minute=requested_rate_per_minute,
            audit_sink=audit_sink,
            now=failed_at,
            events=(RunEvent(occurred_at=failed_at, kind="runner_failure", message=str(exc)),),
        )
    except asyncio.CancelledError:
        stopped_at = now()
        stopped = _finish_with_verdict(
            run,
            samples=tuple(collected),
            verdict=RunVerdict.AUTO_STOPPED,
            requested_rate_per_minute=requested_rate_per_minute,
            audit_sink=audit_sink,
            now=stopped_at,
            events=(
                RunEvent(
                    occurred_at=stopped_at,
                    kind="manual_stop",
                    message="Arrete manuellement par l'utilisateur.",
                ),
            ),
        )
        notify_auto_stop("Test arrete manuellement.", sink=notification_sink)
        return stopped

    verdict = _final_verdict(tuple(collected), bottleneck_detected=bottleneck_notified)
    return _finish_with_verdict(
        run,
        samples=tuple(collected),
        verdict=verdict,
        requested_rate_per_minute=requested_rate_per_minute,
        audit_sink=audit_sink,
        now=now(),
    )


def _final_verdict(
    samples: tuple[IntervalSample, ...], *, bottleneck_detected: bool
) -> RunVerdict:
    if any(sample.error_count > 0 for sample in samples):
        return RunVerdict.DEGRADED
    if bottleneck_detected:
        return RunVerdict.DEGRADED
    return RunVerdict.SUCCESS


def _finish_with_verdict(
    run: LoadRun,
    *,
    samples: tuple[IntervalSample, ...],
    verdict: RunVerdict,
    requested_rate_per_minute: int | None,
    audit_sink: AuditSink,
    now: datetime,
    events: tuple[RunEvent, ...] = (),
) -> LoadRun:
    result = aggregate_samples(
        samples,
        verdict=verdict,
        requested_rate_per_minute=requested_rate_per_minute,
        events=events,
    )
    finished = finish(run, result=result, now=now)
    if isinstance(finished, Err):
        raise UseCaseExecutionError(
            f"Impossible de cloturer le run {run.id} : {finished.error}"
        ) from None
    emit_run_finished(finished.value, sink=audit_sink)
    return finished.value

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'orchestration central du pipeline : consomme le port
#   load_runner, evalue les guards en continu (threshold_guard,
#   degraded_mode), republie via les hooks (metrics, notification,
#   audit), et cloture le run dans tous les cas de sortie possibles
#   (normal, arret automatique, echec technique).
# Pourquoi dans application/pipeline/ (charte) :
# - Seul fichier qui orchestre TOUTES les briques deja construites
#   (guards, hooks, abort, domain/runs/service.py) autour du port
#   load_runner — c'est le coeur du pipeline decrit en ARCHITECTURE.md §4.
# Ce qu'il ne contient PAS :
# - Aucun appel httpx direct (le port load_runner reste la seule
#   abstraction consommee).
# - Aucune construction de LoadPlan/LoadRun initiaux (recus deja
#   construits en parametre — la construction reste du ressort du command
#   appelant, ex. run_request_load.py a venir).
# - Aucune persistance via run_repository : cette fonction retourne le
#   LoadRun final, l'ecriture en base reste a la charge de l'appelant
#   (coherent avec le fait que ports/run_repository.py n'est pas
#   parametre ici — garde ce fichier concentre sur l'execution, pas la
#   persistance).
# Points cles :
# - now: Clock, pas datetime (2026-08-27, correction de bug reel :
#   started_at == finished_at, duree 0.0 min sur TOUS les rapports
#   exportes — voir shared/typing.py::Clock pour le detail complet).
#   now() est appele fraichement a CHAQUE sortie (fin normale, panne
#   RunnerFailureError, arret manuel CancelledError), jamais reutilise
#   depuis avant le `async for` — c'est cette boucle, potentiellement
#   longue de plusieurs minutes, que l'ancienne valeur `now: datetime`
#   figee ne pouvait pas refleter. abort_run() (seuil depasse) recoit le
#   Clock tel quel et fait son propre appel frais, meme principe.
# - Quatre issues de sortie distinctes, toutes cloturees via le meme
#   chemin interne (_finish_with_verdict) : normale (SUCCESS/DEGRADED),
#   arret automatique par seuil (AUTO_STOPPED, via application/pipeline/
#   abort.py, chemin separe car il a sa propre logique de notification),
#   arret manuel (2026-08-25, AUTO_STOPPED egalement — meme verdict que
#   l'arret par seuil, ces deux motifs partagent le meme sens produit
#   "arrete avant la fin", distingues seulement par RunEvent.kind :
#   "threshold_exceeded" vs "manual_stop" — voir ci-dessous), et echec
#   technique (FAILED, capture de RunnerFailureError).
# - Arret manuel (2026-08-25) : capture asyncio.CancelledError, leve par
#   Textual quand l'utilisateur clique "Arreter" (Worker.cancel() sur le
#   worker qui execute ce pipeline, voir screens/request_panel.py et
#   consorts) — le point d'attente actif au moment de l'annulation est
#   TOUJOURS a l'interieur de `async for sample in load_runner.run(...)`
#   (seule veritable suspension de cette boucle), la propagation
#   standard d'asyncio livre donc l'exception ICI, jamais ailleurs dans
#   le pipeline. Volontairement PAS re-levee apres cloture (contrairement
#   a l'usage habituel d'une CancelledError) : ce fichier transforme une
#   demande d'arret utilisateur en une fin de run normale et persistee
#   (samples deja collectes conserves), pas en tache annulee au sens
#   asyncio — l'appelant (application/commands/run_request_load.py et
#   consorts) recoit un LoadRun cloture ordinaire, exactement comme pour
#   un arret automatique par seuil, sans avoir besoin de savoir que
#   l'execution a ete interrompue plutot que menee a terme.
# - bottleneck_notified n'est notifie qu'UNE fois par run (pas a chaque
#   intervalle degrade), mais reste vrai pour le calcul du verdict final
#   meme si le goulot ne persiste pas jusqu'a la fin du run.
# - _final_verdict() : DEGRADED des la premiere erreur ou le premier
#   goulot detecte, jamais reevalue a la baisse si la situation
#   s'ameliore ensuite — un run reste "degrade" une fois qu'il l'a ete.
# - `events` sur _finish_with_verdict() (2026-08-24) : le seul appelant a
#   le renseigner est le bloc `except RunnerFailureError`, avec le message
#   de l'exception (deja phrase par
#   infrastructure/runner/httpx_load_generator.py::_check_reachable()) —
#   avant cela, ce message etait catche puis jete, laissant un run FAILED
#   sans aucune raison consultable nulle part (bug corrige le meme jour).
#   Le chemin SUCCESS/DEGRADED n'a rien a y mettre, events reste a sa
#   valeur par defaut ().
# Comment il sera utilise (apercu) :
# - application/commands/run_request_load.py, run_connection_load.py,
#   run_ramp_load.py (a construire) appellent execute() apres
#   application/pipeline/planner.py::prepare_plan().
#---------------------------------------------------------------------->
