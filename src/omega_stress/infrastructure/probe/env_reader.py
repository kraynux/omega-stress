# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Lecture de fichiers d'information systeme exposes par le noyau (/proc)."""
from __future__ import annotations

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

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Sondage technique unique : memoire totale du systeme, lue depuis
#   /proc/meminfo (pseudo-fichier expose par le noyau Linux).
# Pourquoi dans infrastructure/probe/ (charte) :
# - Lecture de fichier systeme brute, aucune decision.
# Ce qu'il ne contient PAS :
# - Aucun seuil de comparaison (voir domain/load/policies.py::
#   MINIMUM_VIABLE_RAM_MB, consomme par local_probe.py).
# - Aucune dependance a psutil ou bibliotheque tierce : lecture directe
#   du pseudo-fichier, coherent avec la philosophie "rester leger" du
#   projet et son perimetre Linux.
# Points cles :
# - Retourne None plutot que de lever si /proc/meminfo est absent ou
#   illisible : un environnement non standard (conteneur restreint,
#   systeme non-Linux) ne doit jamais faire planter le pre-flight check,
#   seulement degrader la capacite correspondante a MISSING.
# - Nom de fichier interprete au sens large : "environnement systeme"
#   (ce que le noyau expose sur l'etat de la machine), pas uniquement
#   os.environ — aucune variable d'environnement au sens strict n'est lue
#   ici, faute de besoin identifie pour ce cas precis en V1.
# Comment il sera utilise (apercu) :
# - infrastructure/probe/local_probe.py.
#---------------------------------------------------------------------->
