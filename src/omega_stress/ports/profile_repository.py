# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de persistance des profils."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.profiles.models import Profile


class ProfileRepository(Protocol):
    """Port consomme par application/, implemente par
    infrastructure/storage/sqlite/profile_repository.py."""

    def save(self, profile: Profile) -> None: ...

    def get(self, profile_id: str) -> Profile | None: ...

    def list_all(self) -> tuple[Profile, ...]: ...

    def delete(self, profile_id: str) -> None: ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de persistance des Profil, sans presumer du support concret.
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin de application/ (creer, lister, figer, supprimer
#   un profil), pas par l'API SQLite : pas de methode "execute_query()"
#   ou similaire qui trahirait la techno d'infrastructure.
# Ce qu'il ne contient PAS :
# - Aucune implementation (voir
#   infrastructure/storage/sqlite/profile_repository.py, seul endroit ou
#   sqlite3 est importe).
# - Aucune logique de validation : un repository sauvegarde ce qu'on lui
#   donne, il ne valide jamais un Profil lui-meme (domain/profiles/
#   validation.py).
# Points cles :
# - Protocol structurel (PEP 544) plutot qu'ABC : un fake de test n'a pas
#   besoin d'heriter explicitement de ce type pour etre accepte par mypy.
# - delete() est une suppression definitive, distincte d'un archivage
#   (Profile.archived, une donnee metier, pas une operation de
#   repository).
# Comment il sera utilise (apercu) :
# - application/commands/create_profile.py, freeze_profile.py et
#   application/queries/list_profiles.py recoivent une instance de ce port
#   injectee par app/dependency_container.py.
#---------------------------------------------------------------------->
