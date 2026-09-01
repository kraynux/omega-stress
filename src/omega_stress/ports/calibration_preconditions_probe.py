# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de sondage des preconditions de calibrage (CPU/memoire/swap/
load average de la machine, AVANT tout demarrage du serveur local)."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.calibration.models import CalibrationPreconditionsSnapshot


class CalibrationPreconditionsProbe(Protocol):
    """Implemente par infrastructure/calibration/preconditions_probe.py."""

    async def read(self) -> CalibrationPreconditionsSnapshot:
        """Prend une mesure ponctuelle des grandeurs necessaires a
        domain/calibration/validators.py::evaluate_preconditions().
        Async (contrairement a ports/system_sampler.py::SystemSampler) :
        une lecture fiable de CPU/swap demande un court intervalle reel
        entre deux mesures, jamais instantane."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de sondage PONCTUEL (une fois, avant de demarrer un
#   calibrage) — distinct de ports/system_sampler.py::SystemSampler
#   (continu, une fois par intervalle PENDANT un calibrage/run) et de
#   ports/system_probe.py::SystemProbe (une fois, capacites STATIQUES
#   type nombre de coeurs, pas de mesure de charge actuelle).
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (verifier les preconditions avant de
#   demarrer), jamais par psutil/os.getloadavg() eux-memes (prives a
#   l'implementation).
# Ce qu'il ne contient PAS :
# - Aucune decision d'autoriser/refuser le calibrage (voir domain/
#   calibration/validators.py::evaluate_preconditions(), qui consomme le
#   CalibrationPreconditionsSnapshot produit ici).
# Points cles :
# - async (seul port "sondage" async du projet) : lire une charge CPU/
#   swap representative demande un court intervalle reel entre deux
#   appels psutil (voir infrastructure/calibration/preconditions_probe.py)
#   — contrairement a SystemSampler.sample(), qui reste synchrone car
#   appele a un rythme deja regule par la boucle d'execution appelante.
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py appelle read() avant de
#   construire CalibrationLocalServer.
#---------------------------------------------------------------------->
