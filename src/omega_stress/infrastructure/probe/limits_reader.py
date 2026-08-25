# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Lecture des limites systeme de descripteurs de fichiers ouverts."""
from __future__ import annotations

import resource


def read_open_file_limit() -> tuple[int, int]:
    """Retourne (limite douce, limite dure) de descripteurs de fichiers
    ouverts pour le processus courant."""
    return resource.getrlimit(resource.RLIMIT_NOFILE)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Sondage technique unique : limite de descripteurs de fichiers
#   ouverts, pertinente pour la capacite a maintenir de nombreuses
#   connexions simultanees (Test connexions).
# Pourquoi dans infrastructure/probe/ (charte) :
# - Appel systeme direct (module `resource`, specifique POSIX/Linux),
#   aucune decision.
# Ce qu'il ne contient PAS :
# - Aucun seuil de comparaison (voir domain/load/policies.py::
#   MINIMUM_OPEN_FILES_SOFT_LIMIT, consomme par local_probe.py).
# Points cles :
# - Specifique POSIX (module `resource`, absent sous Windows) : coherent
#   avec le perimetre Linux du produit (voir README.md).
# Comment il sera utilise (apercu) :
# - infrastructure/probe/local_probe.py.
#---------------------------------------------------------------------->
