# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Guard 4/4 du pipeline : seuils d'arret, evalues en continu pendant l'execution."""
from __future__ import annotations

from omega_stress.core.results import Result
from omega_stress.domain.errors import ThresholdExceededError
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.load.validators import evaluate_threshold
from omega_stress.domain.runs.models import IntervalSample


def check_threshold(
    sample: IntervalSample, *, thresholds: Thresholds
) -> Result[None, ThresholdExceededError]:
    """Evalue un point de mesure contre les seuils d'arret du plan en
    cours. Appelee a chaque IntervalSample par
    application/pipeline/executor.py, jamais en une seule fois a la fin."""
    observed_error_rate = (
        sample.error_count / sample.request_count if sample.request_count > 0 else 0.0
    )
    return evaluate_threshold(
        observed_error_rate=observed_error_rate,
        observed_p95_latency_ms=sample.p95_latency_ms,
        thresholds=thresholds,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul guard evalue EN CONTINU pendant l'execution (les trois autres ne
#   s'executent qu'une fois, avant le demarrage) : traduit un
#   IntervalSample brut en taux d'erreur, puis delegue integralement la
#   comparaison a domain/load/validators.py::evaluate_threshold().
# Pourquoi dans application/pipeline/guards/ (charte) :
# - Le calcul du taux d'erreur a partir d'un IntervalSample (division)
#   est un detail d'adaptation entre le format de mesure brut et la
#   signature du validateur domaine, pas une regle metier en soi (celle-ci
#   reste entierement dans evaluate_threshold()).
# Ce qu'il ne contient PAS :
# - Aucune decision d'arret (c'est application/pipeline/executor.py qui
#   interprete un Err retourne ici et declenche
#   application/pipeline/abort.py).
# - Aucune agregation multi-intervalles : chaque appel ne voit qu'UN seul
#   IntervalSample, jamais l'historique complet du run (le taux d'erreur
#   evalue est donc celui de l'intervalle courant, pas un cumul depuis le
#   debut — coherent avec Thresholds.max_error_rate pense comme un seuil
#   par intervalle, voir domain/load/models.py::Thresholds).
# Points cles :
# - Division par zero evitee explicitement (request_count == 0 -> taux
#   d'erreur de 0.0, pas d'exception) : un intervalle sans requete n'est
#   pas un echec.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle check_threshold() a chaque
#   IntervalSample recu du port load_runner, avant de le republier via
#   run_progress_notifier.
#---------------------------------------------------------------------->
