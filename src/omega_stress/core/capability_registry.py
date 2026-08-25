# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Registre consolide des capacites (terminal + systeme local)."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_stress.core.capability import Capability
from omega_stress.core.enums import CapabilityStatus
from omega_stress.core.exceptions import CapabilityRegistryError


@dataclass(slots=True)
class CapabilityRegistry:
    """Point de consolidation unique des capacites detectees, quelle que
    soit leur source (voir ARCHITECTURE.md §4, chaine Capacites)."""

    _capabilities: dict[str, Capability] = field(default_factory=dict)

    def register(self, capability: Capability) -> None:
        """Enregistre ou remplace l'etat consolide d'une capacite nommee."""
        self._capabilities[capability.name] = capability

    def get(self, name: str) -> Capability:
        try:
            return self._capabilities[name]
        except KeyError as exc:
            raise CapabilityRegistryError(f"Capacite inconnue : {name!r}") from exc

    def status_of(self, name: str) -> CapabilityStatus:
        return self.get(name).status

    def is_usable(self, name: str) -> bool:
        return self.get(name).is_usable

    def all(self) -> tuple[Capability, ...]:
        return tuple(self._capabilities.values())

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Etape 2 de la chaine Capacites (ARCHITECTURE.md §4) : consolide dans un
#   seul point d'acces les capacites remontees par les sondages bruts
#   (infrastructure/terminal/raw_capabilities.py, infrastructure/probe/).
# Pourquoi dans core/ (charte) :
# - Vocabulaire transverse, sans dependance a la nature de la capacite
#   (terminal ou systeme) ni a la techno de sondage.
# Ce qu'il ne contient PAS :
# - Aucun appel systeme, aucune lecture de variable d'environnement (c'est
#   infrastructure/).
# - Aucune decision d'autorisation d'un run ou d'un profil de rendu (c'est
#   application/pipeline/guards/capability_guard.py, etape 3 de la chaine).
# Points cles :
# - get() leve CapabilityRegistryError pour une capacite jamais enregistree
#   plutot que de retourner un etat par defaut silencieux : une capacite non
#   sondee ne doit jamais etre confondue avec une capacite MISSING connue.
# - is_usable()/status_of() sont de simples raccourcis de lecture au-dessus
#   de get().
# - Pas de mecanisme de rafraichissement automatique en V1 : le registre est
#   repeuple explicitement au demarrage (app/bootstrap.py) et avant chaque
#   run si necessaire (pas de sonde continue, voir plan produit "Portee V1
#   precisee" sur infrastructure/system/local_probe.py).
# Comment il sera utilise (apercu) :
# - app/bootstrap.py cree une instance unique, injectee via
#   app/dependency_container.py.
# - application/pipeline/guards/capability_guard.py et
#   interfaces/tui/rendering/render_profile_resolver.py la consultent en
#   lecture seule.
#---------------------------------------------------------------------->
