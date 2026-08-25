# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Execution d'une requete HTTP unique et mesure de sa latence."""
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass(frozen=True, slots=True)
class RequestOutcome:
    """Resultat brut d'une requete individuelle, avant toute agregation."""

    latency_ms: float
    success: bool


async def perform_request(client: httpx.AsyncClient, url: str) -> RequestOutcome:
    """Emet une requete GET et mesure sa latence. Absorbe toute erreur
    httpx au niveau de CETTE requete (timeout, connexion refusee) en un
    echec compte dans le taux d'erreur de l'intervalle — ne leve jamais :
    c'est le mecanisme normal de detection de degradation/depassement de
    seuil (ARCHITECTURE.md §5.3), pas une panne du generateur lui-meme
    (voir httpx_load_generator.py pour la distinction avec
    RunnerFailureError)."""
    started = time.perf_counter()
    try:
        response = await client.get(url)
        latency_ms = (time.perf_counter() - started) * 1000
        return RequestOutcome(latency_ms=latency_ms, success=response.status_code < 400)
    except httpx.HTTPError:
        latency_ms = (time.perf_counter() - started) * 1000
        return RequestOutcome(latency_ms=latency_ms, success=False)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Emet une requete HTTP unique, mesure sa latence, classe son succes.
# Pourquoi dans infrastructure/runner/ (charte) :
# - Detail d'execution technique unitaire, reutilise par
#   httpx_load_generator.py pour chaque requete d'un intervalle.
# Ce qu'il ne contient PAS :
# - Aucune agregation multi-requetes (voir result_parser.py).
# - Aucune decision d'arret (le taux d'erreur resultant est evalue par
#   application/pipeline/guards/threshold_guard.py, pas ici).
# Points cles :
# - success = status_code < 400 : 2xx/3xx comptent comme succes, 4xx/5xx
#   comme erreur — convention HTTP standard, coherente avec le sens de
#   "erreur" attendu par domain/load/validators.py::evaluate_threshold().
# - Absorbe httpx.HTTPError (timeout, connexion refusee, DNS) en un
#   RequestOutcome(success=False) plutot que de lever : une erreur PONCTUELLE
#   pendant un run fait partie du parcours normal (elle alimente le taux
#   d'erreur de l'intervalle), distincte d'une panne du generateur qui
#   l'empeche de fonctionner DU TOUT (voir httpx_load_generator.py).
# Comment il sera utilise (apercu) :
# - infrastructure/runner/httpx_load_generator.py appelle perform_request()
#   en parallele pour chaque requete d'un intervalle.
#---------------------------------------------------------------------->
