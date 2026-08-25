# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de generation de charge et de publication des mesures d'intervalle."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.runs.models import IntervalSample


class LoadRunner(Protocol):
    """Port consomme par application/pipeline/executor.py, implemente par
    infrastructure/runner/httpx_load_generator.py — seul point du projet
    ou `httpx` est importe."""

    def run(self, plan: LoadPlan, *, target_url: str) -> AsyncIterator[IntervalSample]:
        """Execute le plan et produit un IntervalSample par intervalle
        d'echantillonnage (frequence : domain/load/policies.py::
        SAMPLE_INTERVAL_SECONDS). L'appelant est responsable d'arreter la
        consommation du flux (et donc l'execution) si un guard
        (application/pipeline/guards/threshold_guard.py) l'exige — ce
        Protocol ne prevoit pas de methode stop() separee : fermer le flux
        est le mecanisme d'arret."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat unique de generation de charge, independant du fait qu'elle
#   soit native httpx/asyncio (decision de cadrage V1) ou un futur moteur
#   different.
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (executer un plan, recevoir des
#   mesures), jamais par l'API httpx elle-meme (pas de parametre
#   "httpx.Limits" ou similaire qui fuit un detail d'infrastructure).
# Ce qu'il ne contient PAS :
# - Aucune implementation (voir
#   infrastructure/runner/httpx_load_generator.py).
# - Aucune gestion d'erreur specifique httpx (timeout, DNS, connexion
#   refusee) : l'adaptateur traduit ces exceptions techniques en echec
#   metier (ThresholdExceededError ou RunnerFailureError) avant qu'elles
#   ne remontent a travers ce port (ARCHITECTURE.md §5.3).
# Points cles :
# - Une methode run() qui retourne un flux asynchrone plutot qu'un
#   resultat final unique : coherent avec la publication en continu vers
#   run_progress_notifier (1 point/s) exigee par le plan produit.
# - target_url est une chaine deja resolue (TargetAddress.base_url), pas
#   un objet TargetAddress : ce port ne connait pas le sous-domaine
#   targets, seulement une URL.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py consomme le flux, publie chaque
#   IntervalSample via ports/run_progress_notifier.py, et interroge
#   application/pipeline/guards/threshold_guard.py a chaque iteration.
#---------------------------------------------------------------------->
