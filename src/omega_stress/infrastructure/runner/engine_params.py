# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Calcul des parametres d'execution (cible d'intensite par intervalle) a partir d'un LoadPlan."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import TestFamily
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.policies import SAMPLE_INTERVAL_SECONDS
from omega_stress.domain.load.presets import fixed_rate_preset, ramp_preset


@dataclass(frozen=True, slots=True)
class IntervalTarget:
    """Cible d'intensite pour UN intervalle d'echantillonnage."""

    requests_per_second: float
    concurrency: int


def total_intervals(plan: LoadPlan) -> int:
    """Nombre d'intervalles d'echantillonnage sur la duree totale du plan."""
    return max(1, round(plan.duration.minutes * 60 / SAMPLE_INTERVAL_SECONDS))


def target_for_interval(plan: LoadPlan, interval_index: int) -> IntervalTarget:
    """Cible d'intensite pour l'intervalle `interval_index` (0-based),
    resolue depuis les presets figes (domain/load/presets.py) — jamais
    une valeur calculee independamment ici."""
    if plan.family is TestFamily.CONNECTION:
        connection_preset = fixed_rate_preset(plan.level)
        return IntervalTarget(
            requests_per_second=0.0, concurrency=connection_preset.concurrent_connections
        )

    if plan.family is TestFamily.RAMP:
        peak_preset = ramp_preset(plan.level)
        ratio = _ramp_ratio_at(plan, interval_index)
        return IntervalTarget(
            requests_per_second=(peak_preset.peak_requests_per_minute * ratio) / 60.0,
            concurrency=0,
        )

    request_preset = fixed_rate_preset(plan.level)
    return IntervalTarget(
        requests_per_second=request_preset.requests_per_minute / 60.0, concurrency=0
    )


def _ramp_ratio_at(plan: LoadPlan, interval_index: int) -> float:
    elapsed_seconds = interval_index * SAMPLE_INTERVAL_SECONDS
    cursor = 0.0
    for step in plan.ramp_steps:
        step_duration_seconds = step.duration_minutes * 60
        if elapsed_seconds <= cursor + step_duration_seconds:
            if step_duration_seconds <= 0:
                return step.end_ratio
            progress = (elapsed_seconds - cursor) / step_duration_seconds
            progress = min(1.0, max(0.0, progress))
            return step.start_ratio + (step.end_ratio - step.start_ratio) * progress
        cursor += step_duration_seconds
    return plan.ramp_steps[-1].end_ratio if plan.ramp_steps else 1.0

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit un LoadPlan (family/level/ramp_steps) en cible d'intensite
#   concrete (requetes/seconde ou concurrence) pour un intervalle
#   d'echantillonnage donne — pure fonction du temps ecoule, aucun etat.
# Pourquoi dans infrastructure/runner/ (charte) :
# - Consomme domain/load/presets.py comme seule source de verite pour les
#   valeurs cibles ; ce fichier ne fait que la conversion vers une unite
#   exploitable par le generateur (requetes/seconde plutot que
#   requetes/minute), un detail d'execution technique.
# Ce qu'il ne contient PAS :
# - Aucune valeur de charge en dur (tout vient de domain/load/presets.py).
# - Aucun appel reseau (voir async_worker.py, httpx_load_generator.py).
# Points cles :
# - _ramp_ratio_at() interpole lineairement entre start_ratio et
#   end_ratio de chaque RampStep, proportionnellement au temps ecoule
#   dans l'etape courante — simplification assumee (une vraie montee en
#   charge pourrait suivre une courbe non lineaire, non specifiee par le
#   plan produit).
# - Pour Test connexions, requests_per_second reste a 0.0 : la cible
#   d'intensite est portee par `concurrency`, jamais un debit (voir
#   httpx_load_generator.py pour la traduction en requetes concurrentes).
# Comment il sera utilise (apercu) :
# - infrastructure/runner/httpx_load_generator.py appelle
#   total_intervals() puis target_for_interval() a chaque iteration.
#---------------------------------------------------------------------->
