# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de sondage systeme CONTINU pendant un run (Phase 1
observabilite) — distinct de ports/system_probe.py, explicitement
pre-flight uniquement (sa propre docstring l'exclut d'une supervision
pendant l'execution)."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.runs.models import SystemSnapshot


class SystemSampler(Protocol):
    """Port consomme par infrastructure/runner/httpx_load_generator.py,
    implemente par infrastructure/probe/live_probe.py."""

    def sample(self) -> SystemSnapshot:
        """Prend une photo instantanee des ressources systeme locales
        (CPU generateur/global, memoire, swap, FDs). Ne leve jamais :
        un champ non mesurable reste None plutot que de faire echouer
        le run pour une metrique secondaire."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de sondage systeme appele UNE FOIS PAR INTERVALLE pendant un
#   run, par opposition a ports/system_probe.py (une fois, avant le
#   lancement).
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (obtenir un SystemSnapshot a chaque
#   intervalle), jamais par psutil lui-meme (prive a l'implementation,
#   voir infrastructure/probe/live_probe.py — seul point du projet ou
#   psutil est importe, contrat import-linter dedie).
# Ce qu'il ne contient PAS :
# - Aucune decision d'arret/degradation (voir application/pipeline/,
#   phases suivantes) : ce port se contente de mesurer.
# Points cles :
# - Une seule methode, sans etat expose : l'implementation garde son
#   propre etat interne (ex. psutil.Process() pour un delta CPU correct
#   entre deux appels), jamais le consommateur.
# Comment il sera utilise (apercu) :
# - infrastructure/runner/httpx_load_generator.py::HttpxLoadGenerator
#   appelle sample() a chaque intervalle, juste avant de publier
#   l'IntervalSample.
#---------------------------------------------------------------------->
