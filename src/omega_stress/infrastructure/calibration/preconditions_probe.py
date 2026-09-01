# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation concrete du port CalibrationPreconditionsProbe."""
from __future__ import annotations

import asyncio
import os

import psutil

from omega_stress.domain.calibration.models import CalibrationPreconditionsSnapshot
from omega_stress.infrastructure.probe.env_reader import read_load_average_1min


class LiveCalibrationPreconditionsProbe:
    """Implemente ports/calibration_preconditions_probe.py::
    CalibrationPreconditionsProbe. Seul point du sous-domaine calibration
    (avec infrastructure/probe/) ou psutil est importe — autorise par le
    meme contrat import-linter que infrastructure/probe/live_probe.py
    (source_modules n'exclut pas infrastructure/ elle-meme, voir
    pyproject.toml)."""

    async def read(self) -> CalibrationPreconditionsSnapshot:
        # psutil.cpu_percent(interval=None) mesure un DELTA depuis le
        # dernier appel (voir infrastructure/probe/live_probe.py, meme
        # principe) — un premier appel isole ne serait pas exploitable,
        # d'ou l'amorçage puis la seconde lecture apres une pause reelle
        # courte plutot que le blocage complet de 5s suggere par le
        # document (approximation assumee, voir INFO DEV).
        psutil.cpu_percent(interval=None)
        first_swap = psutil.swap_memory().used
        await asyncio.sleep(1.0)
        cpu_global_percent = psutil.cpu_percent(interval=None)
        second_swap = psutil.swap_memory().used
        memory_available_percent = _memory_available_percent()

        return CalibrationPreconditionsSnapshot(
            cpu_global_percent=cpu_global_percent,
            memory_available_percent=memory_available_percent,
            swap_active_or_growing=second_swap > first_swap,
            load_average_1min=read_load_average_1min(),
            logical_cpu_count=os.cpu_count() or 1,
        )


def _memory_available_percent() -> float | None:
    memory = psutil.virtual_memory()
    if not memory.total:
        return None
    return (memory.available / memory.total) * 100

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Sondage ponctuel des preconditions de calibrage (CPU global, memoire
#   disponible, swap en croissance, load average, nombre de coeurs).
# Pourquoi dans infrastructure/calibration/ (charte) :
# - Implementation concrete d'un port, aucune decision — meme role que
#   infrastructure/probe/local_probe.py pour son propre port.
# Ce qu'il ne contient PAS :
# - Aucun seuil de comparaison (voir domain/calibration/policies.py::
#   CALIBRATION_PRECONDITION_*, consomme par domain/calibration/
#   validators.py::evaluate_preconditions(), jamais ici).
# - Aucune verification "autre calibrage/test actif" : concern PUREMENT
#   applicatif (etat en memoire du processus, voir application/commands/
#   run_calibration.py), jamais un sondage systeme.
# Points cles :
# - read() attend 1 seconde reelle (pas les 5 du document) entre les deux
#   lectures CPU/swap : approximation assumee pour rester reactif a
#   l'ouverture de l'ecran Calibrage — le document parle d'une moyenne
#   sur 5s, ce sondage mesure un delta sur ~1s a la place (angle mort
#   assume, voir plan). swap_active_or_growing ne detecte que la
#   CROISSANCE sur cet intervalle (second_swap > first_swap), jamais
#   "deja significative" (aucun seuil chiffre donne par le document pour
#   cette seconde condition).
# - _memory_available_percent() reprend EXACTEMENT le meme calcul que
#   infrastructure/probe/live_probe.py::LiveSystemSampler.sample()
#   (memory.available / memory.total * 100) : une seule formule, jamais
#   deux versions qui pourraient diverger.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py construit une instance, injectee dans
#   application/commands/run_calibration.py.
#---------------------------------------------------------------------->
