# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Modele generique de capacite, reutilise pour la capacite terminal et la
capacite systeme locale (voir ARCHITECTURE.md §4, chaine Capacites)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import CapabilityStatus


@dataclass(frozen=True, slots=True)
class Capability:
    """Etat consolide d'une capacite (ex. "terminal.color_depth",
    "system.available_fd"), independamment de sa source de sondage."""

    name: str
    status: CapabilityStatus
    detail: str = ""

    @property
    def is_usable(self) -> bool:
        """Une capacite MISSING ou DISQUALIFIED n'est jamais utilisable,
        DEGRADED reste utilisable avec restriction (voir le guard appelant)."""
        return self.status in (CapabilityStatus.AVAILABLE, CapabilityStatus.DEGRADED)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Value object immuable representant l'etat consolide d'UNE capacite,
#   quelle que soit sa nature (terminal ou systeme local).
# Pourquoi dans core/ (charte) :
# - Vocabulaire transverse reutilise par deux sondages distincts
#   (infrastructure/terminal/raw_capabilities.py et infrastructure/probe/) ;
#   ne pas dupliquer une classe Capability par sondage.
# Ce qu'il ne contient PAS :
# - Aucune logique de sondage (c'est infrastructure/terminal/ et
#   infrastructure/probe/).
# - Aucune decision d'autorisation (c'est application/pipeline/guards/
#   capability_guard.py qui interprete is_usable dans son contexte).
# - Pas de mapping "quel profil de rendu pour quelle capacite terminal" :
#   ceci reste une politique de domain/terminal/policies.py.
# Points cles :
# - is_usable() traite DEGRADED comme utilisable (avec restriction) et
#   MISSING/DISQUALIFIED comme jamais utilisables (regle explicite de
#   ARCHITECTURE.md §4 : "Une capacite MISSING ou DISQUALIFIED n'est jamais
#   traitee comme disponible").
# - dataclass frozen+slots : immuable, comparable par valeur, leger.
# Comment il sera utilise (apercu) :
# - core/capability_registry.py stocke des instances de Capability par nom.
# - application/pipeline/guards/capability_guard.py lit is_usable() avant
#   d'autoriser un niveau Violent/Maximum ou un rendu donne.
#---------------------------------------------------------------------->
