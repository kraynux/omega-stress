# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Agregation des resultats de requetes brutes d'un intervalle en IntervalSample."""
from __future__ import annotations

from omega_stress.domain.runs.models import IntervalSample
from omega_stress.infrastructure.runner.async_worker import RequestOutcome


def parse_interval(at_second: float, outcomes: list[RequestOutcome]) -> IntervalSample:
    """Agrege les resultats bruts d'un intervalle en un IntervalSample.
    Un intervalle sans requete (Test connexions au repos, ou palier de
    rampe a 0) produit un echantillon a zero, jamais une erreur."""
    if not outcomes:
        return IntervalSample(
            at_second=at_second,
            observed_rate_per_minute=0.0,
            p50_latency_ms=0.0,
            p95_latency_ms=0.0,
            p99_latency_ms=0.0,
            error_count=0,
            request_count=0,
        )

    latencies = sorted(outcome.latency_ms for outcome in outcomes)
    error_count = sum(1 for outcome in outcomes if not outcome.success)

    return IntervalSample(
        at_second=at_second,
        observed_rate_per_minute=len(outcomes) * 60.0,
        p50_latency_ms=_percentile(latencies, 0.50),
        p95_latency_ms=_percentile(latencies, 0.95),
        p99_latency_ms=_percentile(latencies, 0.99),
        error_count=error_count,
        request_count=len(outcomes),
    )


def _percentile(sorted_values: list[float], fraction: float) -> float:
    """Percentile par indexation directe sur la liste triee — simplification
    assumee (nearest-rank), suffisante pour un intervalle de quelques
    dizaines/centaines de requetes maximum."""
    index = min(len(sorted_values) - 1, round(fraction * (len(sorted_values) - 1)))
    return sorted_values[index]

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul point de conversion RequestOutcome (bruts) -> IntervalSample
#   (domaine), pour un intervalle d'echantillonnage.
# Pourquoi dans infrastructure/runner/ (charte) :
# - Detail d'agregation propre a la sortie du generateur httpx ; produit
#   un objet de domaine (IntervalSample) mais reste lui-meme un detail
#   d'infrastructure (le calcul de percentile est une technique
#   d'implementation, pas une regle metier).
# Ce qu'il ne contient PAS :
# - Aucune agregation MULTI-intervalles (voir
#   domain/runs/service.py::aggregate_samples(), qui combine plusieurs
#   IntervalSample en un LoadResult final — deux echelles differentes).
# Points cles :
# - observed_rate_per_minute extrapole le nombre de requetes de
#   l'intervalle (normalement 1s, SAMPLE_INTERVAL_SECONDS) a une valeur
#   par minute (x60) : suppose implicitement un intervalle d'exactement
#   1 seconde — a revoir si SAMPLE_INTERVAL_SECONDS change un jour.
# - _percentile() utilise une methode "nearest-rank" simple plutot qu'une
#   interpolation lineaire entre rangs : ecart negligeable au volume de
#   requetes par intervalle attendu en V1 (quelques dizaines).
# Comment il sera utilise (apercu) :
# - infrastructure/runner/httpx_load_generator.py appelle parse_interval()
#   a chaque intervalle, juste avant de le publier (yield).
#---------------------------------------------------------------------->
