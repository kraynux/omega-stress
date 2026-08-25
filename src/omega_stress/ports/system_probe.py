# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de sondage des capacites systeme locales (pre-flight check)."""
from __future__ import annotations

from typing import Protocol

from omega_stress.core.capability import Capability


class SystemProbe(Protocol):
    """Port consomme par application/pipeline/guards/capability_guard.py,
    implemente par infrastructure/probe/local_probe.py et
    limits_reader.py."""

    def probe(self) -> tuple[Capability, ...]:
        """Sonde les capacites systeme locales pertinentes au lancement
        d'un run (CPU libre, memoire, limites de fichiers ouverts — voir
        plan produit, "Configuration minimale du generateur"). Controle
        au lancement uniquement (pre-flight), pas une supervision continue
        pendant le run en V1."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de sondage des capacites systeme locales, consolidees ensuite
#   dans core/capability_registry.py.
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (obtenir un ensemble de Capability),
#   jamais par les appels systeme concrets (lecture de /proc, psutil ou
#   equivalent) qui restent prives a l'implementation.
# Ce qu'il ne contient PAS :
# - Aucune decision d'autorisation (c'est
#   application/pipeline/guards/capability_guard.py qui interprete le
#   resultat via core/capability_registry.py).
# - Aucune supervision continue pendant un run : la "Portee V1 precisee"
#   du plan produit limite ce sondage au pre-flight check, pas a une
#   sonde active pendant l'execution (enrichissement explicitement hors
#   perimetre V1).
# Points cles :
# - probe() retourne toutes les capacites en un seul appel plutot qu'une
#   methode par capacite : un seul point d'appel a chaque pre-flight
#   check, plus simple a orchestrer par le guard appelant.
# Comment il sera utilise (apercu) :
# - application/pipeline/guards/capability_guard.py appelle probe() puis
#   alimente core/capability_registry.py avant toute decision.
#---------------------------------------------------------------------->
