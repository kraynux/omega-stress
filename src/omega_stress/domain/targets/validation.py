# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Validation et parsing d'une adresse de cible saisie par l'utilisateur."""
from __future__ import annotations

from urllib.parse import urlsplit

from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.targets.models import TargetAddress


def parse_target_address(raw: str) -> Result[TargetAddress, ValidationError]:
    """Parse et valide une adresse saisie (ex. "https://example.org/api",
    ou "example.org" sans schema explicite, complete en http:// par
    defaut).

    Regles : schema http/https obligatoire une fois complete, hote non
    vide. Ne verifie ni la resolution DNS ni la joignabilite reseau —
    c'est le role du pre-check (application/commands/run_precheck.py), pas
    d'une validation de format pure.
    """
    candidate = raw.strip()
    if not candidate:
        return Err(ValidationError("L'adresse de la cible ne peut pas etre vide."))

    parsed = urlsplit(candidate if "://" in candidate else f"http://{candidate}")

    if parsed.scheme not in ("http", "https"):
        return Err(
            ValidationError(
                f"Schema {parsed.scheme!r} non supporte : seuls http et https sont acceptes."
            )
        )
    if not parsed.hostname:
        return Err(ValidationError(f"Adresse invalide, hote introuvable dans {raw!r}."))

    try:
        address = TargetAddress(
            scheme=parsed.scheme,
            host=parsed.hostname,
            port=parsed.port,
            path=parsed.path or "/",
        )
    except ValueError as exc:
        return Err(ValidationError(str(exc)))

    return Ok(address)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique pour transformer une saisie utilisateur brute
#   (chaine de caracteres) en TargetAddress valide.
# Pourquoi dans domain/targets/ (charte) :
# - Parsing pur base sur urllib.parse (bibliotheque standard, aucune I/O
#   reseau ni resolution DNS) : reste une operation de domaine, pas
#   d'infrastructure.
# Ce qu'il ne contient PAS :
# - Aucune verification de joignabilite reseau, aucune resolution DNS,
#   aucun appel httpx (reserve a infrastructure/runner/ et au pre-check).
# - Aucune persistance : ne cree pas de Target complet (pas d'id, pas de
#   created_at) — seulement l'adresse.
# Points cles :
# - Complete automatiquement "http://" si aucun schema n'est fourni, pour
#   correspondre au parcours "saisie controlee" du panneau de tests
#   (l'utilisateur tape souvent juste un hote).
# - Retourne un Result plutot que de lever : c'est un echec attendu du
#   parcours utilisateur normal (faute de frappe), pas un bug.
# Comment il sera utilise (apercu) :
# - application/commands (creation de profil, ajout de cible manuelle)
#   appellera parse_target_address() avant de construire un Target complet
#   avec id/created_at fournis par l'appelant.
#---------------------------------------------------------------------->
