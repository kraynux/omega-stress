# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Detection en direct d'un goulot d'etranglement local pendant un run."""
from __future__ import annotations

from omega_stress.domain.load.policies import LOCAL_BOTTLENECK_RATIO_THRESHOLD
from omega_stress.domain.runs.models import IntervalSample


def is_local_bottleneck(sample: IntervalSample, *, requested_rate_per_minute: int | None) -> bool:
    """True si le debit observe sur cet intervalle est significativement
    inferieur au debit demande — signal indirect que le generateur local
    est devenu le goulot d'etranglement plutot que la cible elle-meme
    (voir plan produit, "Configuration minimale du generateur"). Controle
    au fil de l'eau, pas une supervision systeme continue (CPU/RAM) —
    portee V1 explicitement limitee au pre-flight check, voir
    ports/system_probe.py."""
    if requested_rate_per_minute is None or requested_rate_per_minute <= 0:
        return False
    threshold = requested_rate_per_minute * LOCAL_BOTTLENECK_RATIO_THRESHOLD
    return sample.observed_rate_per_minute < threshold

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Signal (booleen) de goulot d'etranglement local, evalue par
#   application/pipeline/executor.py a chaque IntervalSample pour decider
#   du verdict final (SUCCESS vs DEGRADED).
# Pourquoi dans application/pipeline/ (charte) :
# - Utilise LOCAL_BOTTLENECK_RATIO_THRESHOLD de domain/load/policies.py
#   (meme constante que domain/reports/builders.py, jamais dupliquee) :
#   ce fichier orchestre l'evaluation EN DIRECT pendant l'execution,
#   distincte de l'evaluation A POSTERIORI faite par
#   domain/reports/builders.py sur le LoadResult final agrege.
# Ce qu'il ne contient PAS :
# - Aucune decision d'arret : contrairement a
#   application/pipeline/guards/threshold_guard.py, un goulot local
#   n'interrompt jamais un run (ce n'est pas un seuil de securite, c'est
#   un signal de diagnostic) — il influence seulement le verdict final,
#   jamais un arret automatique.
# - Aucune supervision systeme active (CPU/RAM en continu) : signal
#   indirect uniquement, base sur l'ecart debit demande/observe (voir
#   plan produit, "Portee V1 precisee" sur infrastructure/system/
#   local_probe.py — un monitoring actif reste hors perimetre V1).
# Points cles :
# - requested_rate_per_minute est None pour un Test connexions (pas de
#   notion de debit demande) : is_local_bottleneck() retourne False dans
#   ce cas, jamais une division par zero ou une erreur.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py verifie is_local_bottleneck() sur
#   chaque IntervalSample pour decider si le verdict final doit etre
#   RunVerdict.DEGRADED plutot que SUCCESS.
#---------------------------------------------------------------------->
