# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Transitions d'etat d'un LoadRun (pas l'execution elle-meme, voir application/pipeline/)."""
from __future__ import annotations

from datetime import datetime

from omega_stress.core.enums import RunVerdict
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.runs.models import IntervalSample, LoadResult, LoadRun, RunEvent


def aggregate_samples(
    samples: tuple[IntervalSample, ...],
    *,
    verdict: RunVerdict,
    requested_rate_per_minute: int | None,
    events: tuple[RunEvent, ...] = (),
) -> LoadResult:
    """Agrege une serie d'IntervalSample en un LoadResult final.

    Simplification assumee pour la V1 : p50 est la moyenne des p50 par
    intervalle, p95/p99 sont le MAXIMUM observe par intervalle (lecture
    prudente plutot qu'une moyenne, qui masquerait un pic ponctuel isole).
    Une agregation statistiquement rigoureuse necessiterait les latences
    individuelles brutes de chaque requete, pas seulement les percentiles
    deja agreges par intervalle — infrastructure/runner/result_parser.py
    pourra fournir un calcul plus precis plus tard si un besoin est
    confirme, sans changer la forme de LoadResult.

    `events` transite tel quel vers le LoadResult produit : cette fonction
    ne decide jamais quels evenements sont pertinents (c'est a l'appelant,
    qui seul connait la raison d'un arret automatique ou d'un echec
    technique, de les construire — voir application/pipeline/abort.py et
    application/pipeline/executor.py).
    """
    if not samples:
        return LoadResult(
            verdict=verdict,
            requested_rate_per_minute=requested_rate_per_minute,
            observed_rate_per_minute=None,
            p50_latency_ms=None,
            p95_latency_ms=None,
            p99_latency_ms=None,
            error_count=0,
            total_requests=0,
            events=events,
            samples=samples,
        )

    return LoadResult(
        verdict=verdict,
        requested_rate_per_minute=requested_rate_per_minute,
        observed_rate_per_minute=sum(s.observed_rate_per_minute for s in samples) / len(samples),
        p50_latency_ms=sum(s.p50_latency_ms for s in samples) / len(samples),
        p95_latency_ms=max(s.p95_latency_ms for s in samples),
        p99_latency_ms=max(s.p99_latency_ms for s in samples),
        error_count=sum(s.error_count for s in samples),
        total_requests=sum(s.request_count for s in samples),
        events=events,
        samples=samples,
    )


def finish(run: LoadRun, *, result: LoadResult, now: datetime) -> Result[LoadRun, ValidationError]:
    """Cloture un run avec son resultat. Un run deja termine ne peut pas
    etre reclos (regle de coherence d'etat, pas une regle de securite)."""
    if run.finished_at is not None:
        return Err(ValidationError(f"Le run {run.id} est deja termine."))

    return Ok(
        LoadRun(
            id=run.id,
            profile_id=run.profile_id,
            target_id=run.target_id,
            family=run.family,
            level=run.level,
            started_at=run.started_at,
            finished_at=now,
            result=result,
            notes=run.notes,
            is_precheck=run.is_precheck,
        )
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - aggregate_samples() : reduit un flux d'IntervalSample en un LoadResult
#   final, quel que soit le verdict retenu par l'appelant.
# - finish() : l'unique transition d'etat non triviale d'un LoadRun, la
#   cloture (started -> finished avec resultat).
# Pourquoi dans domain/runs/ (charte) :
# - Deux fonctions pures, sans I/O : aggregate_samples() ne decide pas du
#   verdict (recu en parametre, decide par le pipeline selon le contexte
#   — seuil depasse, erreurs observees, etc.), elle se contente de reduire
#   les mesures.
# Ce qu'il ne contient PAS :
# - Aucune fonction start() : le demarrage d'un run est un simple acte de
#   construction (LoadRun(id=..., started_at=now, finished_at=None)), pas
#   une transition avec regle a verifier — application/pipeline/planner.py
#   construit directement le LoadRun initial.
# - Aucun declenchement d'arret automatique (c'est
#   application/pipeline/abort.py, qui appelle finish() avec un
#   LoadResult au verdict AUTO_STOPPED une fois la decision prise).
# - Aucune ecriture en base : persister le run termine reste le role
#   d'infrastructure/storage/sqlite/run_repository.py.
# Points cles :
# - finish() est la seule maniere valide de clore un run dans ce module :
#   un appelant qui construirait un LoadRun "termine" directement (sans
#   passer par finish()) contourne la garde "deja termine" — a eviter en
#   application/, toujours passer par ce service.
# - aggregate_samples() retourne un LoadResult a champs None si `samples`
#   est vide (run interrompu avant le premier intervalle) plutot que de
#   lever : un run sans aucune mesure reste un resultat valide a afficher,
#   pas une erreur.
# - `events` (2026-08-24) : simple relai vers LoadResult.events, jamais
#   construit ici — seul l'appelant (abort.py pour un depassement de
#   seuil, executor.py pour un RunnerFailureError) connait la raison
#   exacte a transmettre.
# - LoadResult.samples (2026-08-24) recoit exactement le meme tuple que le
#   parametre `samples` de cette fonction : deja recu pour calculer les
#   agregats, desormais aussi conserve tel quel plutot que jete apres
#   usage. Vrai meme dans la branche vide (`samples=samples` avec un tuple
#   vide) : coherent avec l'invariant deja documente juste au-dessus
#   (LoadResult reste valide sans mesure, jamais une erreur).
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle aggregate_samples() puis
#   finish() a la fin normale d'un run.
# - application/pipeline/abort.py fait de meme avec verdict=AUTO_STOPPED
#   lors d'un arret sur seuil depasse.
#---------------------------------------------------------------------->
