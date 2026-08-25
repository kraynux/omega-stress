# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites et value objects du sous-domaine targets : adresse, cible, cible epinglee."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TargetAddress:
    """Adresse validee d'une cible HTTP. A construire via
    domain/targets/validation.py::parse_target_address — le constructeur
    ne fait qu'une verification minimale de coherence (voir __post_init__),
    pas le parsing complet d'une saisie utilisateur brute."""

    scheme: str
    host: str
    port: int | None = None
    path: str = "/"

    def __post_init__(self) -> None:
        if self.scheme not in ("http", "https"):
            raise ValueError(f"scheme doit etre 'http' ou 'https', recu {self.scheme!r}")
        if not self.host:
            raise ValueError("host ne peut pas etre vide")

    @property
    def base_url(self) -> str:
        port_part = f":{self.port}" if self.port is not None else ""
        return f"{self.scheme}://{self.host}{port_part}{self.path}"


@dataclass(frozen=True, slots=True)
class Target:
    """Cible utilisable pour un test, epinglee ou non."""

    id: str
    address: TargetAddress
    created_at: datetime
    tags: tuple[str, ...] = ()
    notes: str = ""
    last_used_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class PinnedTarget:
    """Cible epinglee : implique une autorisation deja confirmee au moment
    de l'epinglage (ARCHITECTURE.md §7) — son existence dispense
    l'utilisateur de recocher la case de confirmation a chaque run sur
    cette cible."""

    target: Target
    pinned_at: datetime
    authorized_at: datetime

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - TargetAddress : value object d'adresse HTTP validee.
# - Target : cible generique (epinglee ou non), utilisable dans un plan.
# - PinnedTarget : cible epinglee, portant la preuve d'autorisation
#   confirmee.
# Pourquoi dans domain/targets/ (charte) :
# - Entites/VO metier purs, aucune I/O (pas de resolution DNS, pas de
#   requete reseau — voir Ce qu'il ne contient PAS).
# Ce qu'il ne contient PAS :
# - Aucun parsing de saisie utilisateur brute (voir
#   domain/targets/validation.py).
# - Aucune verification reseau (joignabilite, DNS) : c'est le role du
#   pre-check (application/commands/run_precheck.py), pas de ce fichier.
# - Aucune horloge par defaut cachee (created_at/pinned_at/authorized_at
#   sont toujours des parametres explicites, jamais un
#   datetime.now() implicite dans un default_factory) : coherent avec
#   shared/clock.py, qui fournira l'heure injectable aux appelants.
# Points cles :
# - PinnedTarget.authorized_at != PinnedTarget.pinned_at dans le cas
#   general (le champ existe separement pour permettre une future
#   re-confirmation sans re-epingler), mais domain/targets/service.py::pin
#   les fixe actuellement a la meme valeur au moment de l'epinglage.
# - TargetAddress.__post_init__ leve ValueError (pas ValidationError) :
#   c'est un garde-fou de coherence de bas niveau pour un objet construit
#   directement par du code interne (ex. tests, repository), distinct du
#   Result[TargetAddress, ValidationError] que retourne
#   parse_target_address() pour une saisie utilisateur.
# Comment il sera utilise (apercu) :
# - domain/targets/service.py::pin() produit un PinnedTarget a partir d'un
#   Target.
# - domain/load/validators.py::validate_plan() lit
#   target_authorization_confirmed (porte au niveau du LoadPlan, pas
#   directement ici) pour decider si un run peut demarrer.
#---------------------------------------------------------------------->
