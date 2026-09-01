# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Guard 4/5 du pipeline : seuils d'arret cote cible, evalues en continu
pendant l'execution — par intervalle (check_threshold) et par fenetre
glissante (check_sliding_window, Phase 2 garde-fous)."""
from __future__ import annotations

from collections.abc import Sequence

from omega_stress.core.results import Result
from omega_stress.domain.errors import ThresholdExceededError
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.load.validators import evaluate_sliding_window, evaluate_threshold
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


def check_sliding_window(
    samples: Sequence[IntervalSample],
) -> Result[None, ThresholdExceededError]:
    """Evalue l'HISTORIQUE complet des samples deja collectes contre les
    seuils de fenetre glissante de domain/load/policies.py (Phase 2
    garde-fous) — contrairement a check_threshold() ci-dessus, attrape
    une degradation qui reste sous le seuil PAR INTERVALLE mais
    s'accumule sur la duree. Appelee juste apres check_threshold() a
    chaque IntervalSample par application/pipeline/executor.py."""
    if not samples:
        return evaluate_sliding_window(samples, now_second=0.0)
    return evaluate_sliding_window(samples, now_second=samples[-1].at_second)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Guards evalues EN CONTINU pendant l'execution (les autres guards du
#   pipeline ne s'executent qu'une fois, avant le demarrage) : traduisent
#   le format de mesure brut (IntervalSample/historique) vers les
#   validateurs purs de domain/load/validators.py, sans jamais dupliquer
#   leur logique de comparaison ici.
# Pourquoi dans application/pipeline/guards/ (charte) :
# - Adaptation entre le format de mesure brut et la signature des
#   validateurs domaine, pas une regle metier en soi (celle-ci reste
#   entierement dans evaluate_threshold()/evaluate_sliding_window()).
# Ce qu'il ne contient PAS :
# - Aucune decision d'arret (c'est application/pipeline/executor.py qui
#   interprete un Err retourne ici et declenche
#   application/pipeline/abort.py).
# - Aucun seuil chiffre (voir domain/load/policies.py et
#   domain/load/models.py::Thresholds).
# Points cles :
# - check_threshold() : division par zero evitee explicitement
#   (request_count == 0 -> taux d'erreur de 0.0, pas d'exception) — ne
#   regarde qu'UN SEUL IntervalSample (l'intervalle courant), coherent
#   avec Thresholds.max_error_rate pense comme un seuil par intervalle.
# - check_sliding_window() (Phase 2) : regarde au contraire tout
#   l'historique deja collecte — evaluate_sliding_window() filtre
#   lui-meme les samples pertinents par fenetre, ce guard se contente de
#   fournir `now_second` (le dernier at_second connu). Liste vide geree
#   explicitement (now_second=0.0, jamais un IndexError sur samples[-1]).
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle check_threshold() PUIS
#   check_sliding_window() a chaque IntervalSample recu du port
#   load_runner, avant de le republier via run_progress_notifier.
#---------------------------------------------------------------------->
