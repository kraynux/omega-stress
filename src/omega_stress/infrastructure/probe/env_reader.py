# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Lecture de fichiers d'information systeme exposes par le noyau (/proc)."""
from __future__ import annotations

import os
from pathlib import Path

_MEMINFO_PATH = Path("/proc/meminfo")


def read_total_memory_mb() -> int | None:
    """Lit la memoire totale (Mo) depuis /proc/meminfo. Retourne None si
    le fichier est absent (systeme non-Linux, environnement restreint) —
    jamais une erreur : l'absence de mesure est un cas normal a gerer par
    l'appelant (voir local_probe.py, qui produit alors une capacite
    MISSING plutot que de planter)."""
    if not _MEMINFO_PATH.exists():
        return None
    try:
        for line in _MEMINFO_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                parts = line.split()
                return int(parts[1]) // 1024
    except OSError:
        return None
    return None


def read_load_average_1min() -> float | None:
    """Lit la charge moyenne systeme sur 1 minute (os.getloadavg()[0],
    wrapper stdlib autour de l'appel POSIX getloadavg()). Retourne None
    si indisponible (systeme non-POSIX) — jamais une erreur, meme
    convention que read_total_memory_mb()."""
    try:
        return os.getloadavg()[0]
    except OSError:
        return None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - read_total_memory_mb() : memoire totale du systeme, lue depuis
#   /proc/meminfo (pseudo-fichier expose par le noyau Linux).
# - read_load_average_1min() (2026-09-01, calibrage) : charge moyenne
#   systeme sur 1 minute, via le wrapper stdlib os.getloadavg().
# Pourquoi dans infrastructure/probe/ (charte) :
# - Lecture de fichier/appel systeme brut, aucune decision.
# Ce qu'il ne contient PAS :
# - Aucun seuil de comparaison (voir domain/load/policies.py::
#   MINIMUM_VIABLE_RAM_MB, consomme par local_probe.py ; domain/
#   calibration/policies.py::CALIBRATION_PRECONDITION_*, consomme par
#   infrastructure/calibration/preconditions_probe.py).
# - Aucune dependance a psutil ou bibliotheque tierce : lecture directe
#   du pseudo-fichier ou de l'appel POSIX, coherent avec la philosophie
#   "rester leger" du projet et son perimetre Linux.
# Points cles :
# - Retourne None plutot que de lever si la mesure est indisponible
#   (conteneur restreint, systeme non-Linux/non-POSIX) : un environnement
#   non standard ne doit jamais faire planter le pre-flight check ni le
#   calibrage, seulement degrader la capacite/precondition correspondante.
# - Nom de fichier interprete au sens large : "environnement systeme" (ce
#   que le noyau expose sur l'etat de la machine), pas uniquement
#   os.environ.
# Comment il sera utilise (apercu) :
# - infrastructure/probe/local_probe.py consomme read_total_memory_mb().
# - infrastructure/calibration/preconditions_probe.py consomme
#   read_load_average_1min().
#---------------------------------------------------------------------->
