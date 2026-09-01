# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Arret automatique d'un run en cours suite a un depassement de seuil."""
from __future__ import annotations

from omega_stress.application.exceptions import AbortError
from omega_stress.core.enums import RunVerdict
from omega_stress.core.results import Err
from omega_stress.domain.errors import ThresholdExceededError
from omega_stress.domain.runs.models import IntervalSample, LoadRun, RunEvent
from omega_stress.domain.runs.service import aggregate_samples, finish
from omega_stress.shared.typing import Clock


def abort_run(
    run: LoadRun,
    *,
    samples: tuple[IntervalSample, ...],
    reason: ThresholdExceededError,
    now: Clock,
) -> LoadRun:
    """Cloture un run par arret automatique (verdict AUTO_STOPPED), suite
    a un ThresholdExceededError detecte par
    application/pipeline/guards/threshold_guard.py ou resource_guard.py
    pendant l'execution.

    Nomme "abort" et non "rollback" (contrairement au gabarit omega-fire) :
    un run de charge deja execute ne se defait pas comme une regle
    firewall appliquee a tort — l'action possible est d'arreter le run en
    cours, jamais d'annuler retroactivement ce qui a deja ete envoye a la
    cible (voir ARCHITECTURE.md §0).
    """
    closed_at = now()
    event = RunEvent(occurred_at=closed_at, kind=reason.signal, message=str(reason))
    result = aggregate_samples(
        samples,
        verdict=RunVerdict.AUTO_STOPPED,
        requested_rate_per_minute=None,
        events=(event,),
    )
    finished = finish(run, result=result, now=closed_at)
    if isinstance(finished, Err):
        # Un run en cours d'execution ne devrait jamais etre deja
        # `finished_at` non-None a ce stade : si finish() refuse quand
        # meme, c'est un bug d'invariant du pipeline, pas un echec metier
        # attendu — d'ou une exception plutot qu'un Result ici.
        raise AbortError(
            f"Impossible de cloturer le run {run.id} apres arret automatique : "
            f"{finished.error}"
        ) from None
    return finished.value

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Cloture un run interrompu en cours d'execution suite a un depassement
#   de seuil, avec le verdict AUTO_STOPPED.
# Pourquoi dans application/pipeline/ (charte) :
# - Orchestre domain/runs/service.py::aggregate_samples()/finish(), point
#   d'integration entre le guard qui a detecte le depassement
#   (threshold_guard) et la cloture effective du run.
# Ce qu'il ne contient PAS :
# - Aucune evaluation de seuil (deja faite par
#   application/pipeline/guards/threshold_guard.py, appelant de cette
#   fonction).
# - Aucune ecriture en base : persister le run cloture reste le role
#   d'infrastructure/storage/sqlite/run_repository.py, appele par
#   application/pipeline/executor.py apres avoir recu le LoadRun retourne
#   ici.
# Points cles :
# - requested_rate_per_minute=None passe a aggregate_samples() : le debit
#   demande initial est deja porte par le LoadPlan/profil, pas par ce
#   point d'arret — a reconsiderer si l'affichage du verdict AUTO_STOPPED
#   a besoin d'afficher l'ecart precis (le run_dto expose deja
#   observed_rate_per_minute quel que soit le verdict).
# - AbortError (application/exceptions.py) n'est levee que dans un cas qui
#   ne devrait jamais se produire en pratique (finish() refusant un run
#   deja marque termine) : un vrai garde-fou de bug, pas un chemin normal.
# - `reason` (2026-08-24) : converti en RunEvent(kind=reason.signal) et
#   transmis a aggregate_samples(), pour que la raison precise de
#   l'arret automatique survive au-dela de la notification live
#   (notify_auto_stop, ephemere) et reste consultable dans le detail du
#   run et l'export — avant cela, `reason` n'etait utilise que pour cette
#   notification et disparaissait ensuite. reason.signal (Phase 2 garde-
#   fous, domain/errors.py::ThresholdExceededError) vaut "threshold_exceeded"
#   par defaut (comportement historique inchange) ou un signal precis
#   (ex. "window_error_rate_exceeded", "generator_cpu_exceeded") pour un
#   arret declenche par les nouveaux guards — RunEvent.kind reste donc
#   toujours "structure" (distinguable programmatiquement), jamais un
#   seul libelle generique pour toute cause d'arret.
# - now: Clock, pas datetime (2026-08-27, correction de bug reel :
#   started_at == finished_at, duree 0.0 min sur TOUS les rapports
#   exportes — voir shared/typing.py::Clock pour le detail complet) :
#   `closed_at = now()` est appele UNE FOIS ici, fraichement, au moment
#   reel de l'arret automatique (pas la valeur figee capturee par
#   l'appelant avant le debut du run) — reutilise pour l'event ET pour
#   finish(), jamais deux appels a now() qui produiraient deux instants
#   legerement differents pour la meme cloture.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle abort_run() des que
#   threshold_guard.check_threshold() retourne un Err.
#---------------------------------------------------------------------->
