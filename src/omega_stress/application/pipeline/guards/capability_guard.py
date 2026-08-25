# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Guard 3/4 du pipeline : capacite systeme suffisante (ARCHITECTURE.md §4)."""
from __future__ import annotations

from omega_stress.application.exceptions import CapabilityUnavailableError
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.results import Err, Ok, Result


def check_capability(
    capability_name: str, *, capability_registry: CapabilityRegistry
) -> Result[None, CapabilityUnavailableError]:
    """Refuse le demarrage si la capacite nommee (ex. "system.available_fd")
    n'est pas utilisable, d'apres le registre deja peuple par un pre-flight
    check (infrastructure/probe/, voir ARCHITECTURE.md §4, chaine
    Capacites)."""
    if not capability_registry.is_usable(capability_name):
        capability = capability_registry.get(capability_name)
        return Err(
            CapabilityUnavailableError(
                f"Capacite {capability_name!r} indisponible (statut : {capability.status.value})."
            )
        )
    return Ok(None)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Troisieme etape obligatoire du pipeline : verifie que le systeme
#   local peut tenir la charge demandee, via core/capability_registry.py
#   deja consolide.
# Pourquoi dans application/pipeline/guards/ (charte) :
# - Consulte core/capability_registry.py (etat consolide, pas de
#   sondage direct ici) : ce guard ne fait aucun appel systeme lui-meme,
#   c'est infrastructure/probe/ qui a deja peuple le registre en amont
#   (typiquement au demarrage de l'application ou juste avant un run
#   Haut/Maximum, voir plan produit "Configuration minimale du
#   generateur").
# Ce qu'il ne contient PAS :
# - Aucun sondage systeme (infrastructure/probe/local_probe.py,
#   limits_reader.py).
# - Aucune decision de QUAND repeupler le registre : ce guard consulte
#   l'etat tel qu'il est au moment de l'appel, la fraicheur du sondage
#   est de la responsabilite de l'appelant (planner.py ou le command
#   run_*_load).
# Points cles :
# - Retourne CapabilityUnavailableError (application/exceptions.py), pas
#   une DomainError : coherent avec ARCHITECTURE.md §5.2, qui classe cette
#   famille d'echec cote application (la capacite systeme n'est pas une
#   notion du domaine metier du test de charge lui-meme).
# - Leve une CapabilityRegistryError (via
#   core/capability_registry.py::get()) si capability_name n'a jamais ete
#   enregistre — un bug d'appel, pas un refus normal, laisse remonter tel
#   quel plutot que d'etre capture ici.
# Comment il sera utilise (apercu) :
# - application/pipeline/planner.py appelle ce guard pour chaque capacite
#   pertinente (ex. "system.available_fd") avant de construire le plan
#   pour un niveau Haut/Maximum.
#---------------------------------------------------------------------->
