# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Guard 5/5 du pipeline : ressources locales du generateur (CPU/memoire/
FDs), evaluees en continu pendant l'execution (Phase 2 garde-fous) —
distinct de capability_guard.py, qui ne verifie qu'une fois avant le
demarrage (pre-flight, capacites STATIQUES type nombre de coeurs)."""
from __future__ import annotations

from collections.abc import Sequence

from omega_stress.core.results import Result
from omega_stress.domain.errors import ThresholdExceededError
from omega_stress.domain.load.validators import evaluate_generator_resources
from omega_stress.domain.runs.models import IntervalSample


def check_generator_resources(
    samples: Sequence[IntervalSample],
) -> Result[None, ThresholdExceededError]:
    """Evalue l'historique des samples deja collectes contre les seuils
    de ressources generateur de domain/load/policies.py (CPU soutenu,
    memoire disponible, descripteurs de fichiers — voir
    domain/runs/models.py::SystemSnapshot, Phase 1 observabilite).
    Appelee juste apres threshold_guard.py::check_sliding_window() a
    chaque IntervalSample par application/pipeline/executor.py."""
    return evaluate_generator_resources(samples)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul guard qui protege le GENERATEUR lui-meme (les 4 autres
#   protegent la cible ou verifient une condition de lancement) — miroir
#   direct de la separation du document produit ("arret par erreurs"
#   vs "arret locale").
# Pourquoi dans application/pipeline/guards/ (charte) :
# - Adaptation entre le format de mesure brut et la signature du
#   validateur domaine, meme raisonnement que threshold_guard.py — toute
#   la logique de comparaison aux seuils reste dans
#   domain/load/validators.py::evaluate_generator_resources().
# Ce qu'il ne contient PAS :
# - Aucun sondage systeme (infrastructure/probe/live_probe.py, deja
#   consomme en amont par infrastructure/runner/httpx_load_generator.py
#   pour produire IntervalSample.system).
# - Aucune decision d'arret (c'est application/pipeline/executor.py qui
#   interprete un Err retourne ici et declenche
#   application/pipeline/abort.py).
# Points cles :
# - Un fonction quasi transparente (delegue integralement) : garde
#   volontairement une couche fine plutot que d'appeler
#   evaluate_generator_resources() directement depuis executor.py, pour
#   rester coherent avec le patron des 4 autres guards (chacun sa
#   fonction check_*() dediee dans application/pipeline/guards/).
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle check_generator_resources()
#   apres check_sliding_window(), a chaque IntervalSample.
#---------------------------------------------------------------------->
