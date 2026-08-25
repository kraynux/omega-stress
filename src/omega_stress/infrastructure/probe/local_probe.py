# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation concrete du port SystemProbe : sondage local pre-flight."""
from __future__ import annotations

import os
from collections.abc import Iterable

from omega_stress.core.capability import Capability
from omega_stress.core.enums import CapabilityStatus
from omega_stress.domain.load.policies import (
    MINIMUM_OPEN_FILES_SOFT_LIMIT,
    MINIMUM_VIABLE_CPU_COUNT,
    MINIMUM_VIABLE_RAM_MB,
)
from omega_stress.infrastructure.probe.env_reader import read_total_memory_mb
from omega_stress.infrastructure.probe.limits_reader import read_open_file_limit

CPU_CAPABILITY = "system.cpu_count"
MEMORY_CAPABILITY = "system.memory"
OPEN_FILES_CAPABILITY = "system.open_files"
LOAD_CAPACITY_CAPABILITY = "system.load_capacity"


def probe_system_capabilities() -> tuple[Capability, ...]:
    """Sonde CPU, memoire et limite de descripteurs ouverts, et produit
    en plus une capacite agregee `system.load_capacity` consommee par
    application/pipeline/guards/capability_guard.py (voir plan produit,
    "Configuration minimale du generateur" — controle au lancement
    uniquement, pas une supervision continue en V1)."""
    cpu_count = os.cpu_count() or 1
    soft_limit, _hard_limit = read_open_file_limit()
    total_memory_mb = read_total_memory_mb()

    cpu = Capability(
        name=CPU_CAPABILITY,
        status=(
            CapabilityStatus.AVAILABLE
            if cpu_count >= MINIMUM_VIABLE_CPU_COUNT
            else CapabilityStatus.DEGRADED
        ),
        detail=f"{cpu_count} coeur(s) detecte(s)",
    )
    open_files = Capability(
        name=OPEN_FILES_CAPABILITY,
        status=(
            CapabilityStatus.AVAILABLE
            if soft_limit >= MINIMUM_OPEN_FILES_SOFT_LIMIT
            else CapabilityStatus.DEGRADED
        ),
        detail=f"limite douce de {soft_limit} descripteurs",
    )
    if total_memory_mb is not None:
        memory = Capability(
            name=MEMORY_CAPABILITY,
            status=(
                CapabilityStatus.AVAILABLE
                if total_memory_mb >= MINIMUM_VIABLE_RAM_MB
                else CapabilityStatus.DEGRADED
            ),
            detail=f"{total_memory_mb} Mo detectes",
        )
    else:
        memory = Capability(
            name=MEMORY_CAPABILITY, status=CapabilityStatus.MISSING, detail="non mesurable"
        )

    individual = (cpu, open_files, memory)
    overall = Capability(
        name=LOAD_CAPACITY_CAPABILITY,
        status=_worst_status(c.status for c in individual),
        detail="agregat de " + ", ".join(c.name for c in individual),
    )
    return (*individual, overall)


def _worst_status(statuses: Iterable[CapabilityStatus]) -> CapabilityStatus:
    ordered = list(statuses)
    if any(s is CapabilityStatus.MISSING for s in ordered):
        return CapabilityStatus.MISSING
    if any(s is CapabilityStatus.DISQUALIFIED for s in ordered):
        return CapabilityStatus.DISQUALIFIED
    if any(s is CapabilityStatus.DEGRADED for s in ordered):
        return CapabilityStatus.DEGRADED
    return CapabilityStatus.AVAILABLE


class LocalSystemProbe:
    """Implemente ports/system_probe.py::SystemProbe."""

    def probe(self) -> tuple[Capability, ...]:
        return probe_system_capabilities()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Sonde les capacites systeme locales pertinentes au lancement d'un run
#   (CPU, memoire, descripteurs ouverts), classees selon les seuils de
#   domain/load/policies.py, et produit une capacite agregee
#   "system.load_capacity" utilisee par
#   application/pipeline/guards/capability_guard.py (voir
#   application/commands/run_request_load.py et les commands
#   equivalents, qui referencent ce meme nom).
# Pourquoi dans infrastructure/probe/ (charte) :
# - Orchestre des sondages techniques (env_reader.py, limits_reader.py,
#   os.cpu_count()) et compare a des seuils DEFINIS AILLEURS
#   (domain/load/policies.py) — ne redefinit jamais un seuil chiffre en
#   dur ici.
# Ce qu'il ne contient PAS :
# - Aucun seuil numerique en dur (voir domain/load/policies.py).
# - Aucune supervision continue pendant un run (portee V1 explicitement
#   limitee au pre-flight check, voir docstring et plan produit).
# Points cles :
# - _worst_status() definit l'ordre de gravite MISSING > DISQUALIFIED >
#   DEGRADED > AVAILABLE pour l'agregation : une seule capacite MISSING
#   suffit a rendre "system.load_capacity" MISSING dans son ensemble.
# - Les quatre constantes de nom de capacite (CPU_CAPABILITY, etc.) sont
#   exportees pour que les tests (et un futur ecran de diagnostic) n'aient
#   pas a recopier les chaines litterales.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py injecte LocalSystemProbe() dans le
#   pre-flight check avant un lancement Haut/Maximum ; le registre
#   consolide (core/capability_registry.py) est repeuple depuis son
#   resultat juste avant l'appel a capability_guard.check_capability().
#---------------------------------------------------------------------->
