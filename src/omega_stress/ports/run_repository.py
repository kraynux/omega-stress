# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de persistance et d'historique des runs."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.runs.models import LoadRun


class RunRepository(Protocol):
    """Port consomme par application/, implemente par
    infrastructure/storage/sqlite/run_repository.py."""

    def save(self, run: LoadRun) -> None: ...

    def get(self, run_id: str) -> LoadRun | None: ...

    def list_history(
        self,
        *,
        target_id: str | None = None,
        profile_id: str | None = None,
        limit: int = 50,
    ) -> tuple[LoadRun, ...]: ...

    def clear(self) -> None: ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de persistance des runs et de leur historique filtrable.
# Pourquoi dans ports/ (charte) :
# - Defini par les besoins du plan produit ("filtrer par cible, profil,
#   date, type" — la date est couverte par le tri implicite de
#   list_history(), pas un parametre supplementaire en V1, faute de
#   filtre de plage de dates precise dans le plan).
# Ce qu'il ne contient PAS :
# - Aucune implementation concrete.
# - Aucun filtre par "type" de test explicite ici : les appelants peuvent
#   filtrer sur le resultat de list_history() cote application si besoin,
#   pour ne pas alourdir le port d'une combinatoire de parametres non
#   confirmee par le plan produit.
# Points cles :
# - save() sert aussi bien a creer (run en cours, finished_at=None) qu'a
#   mettre a jour un run existant (apres domain/runs/service.py::finish()) :
#   pas de create()/update() distincts, l'idempotence par id est de la
#   responsabilite de l'implementation SQLite (upsert).
# - list_history() est triee du plus recent au plus ancien par
#   l'implementation (pas garanti par ce Protocol lui-meme, a documenter
#   et tester au niveau de l'adaptateur concret).
# - clear() (2026-08-24) : purge complete et irreversible de l'historique,
#   demandee explicitement pour l'ecran Reglages ("Vider l'historique").
#   Aucun filtre (contrairement a list_history()) : une purge partielle
#   n'a pas ete demandee, garder le port minimal tant qu'elle ne l'est
#   pas. Exige une confirmation dediee cote ecran (voir screens/
#   confirm.py), jamais silencieuse.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py (sauvegarde), application/queries/
#   list_history.py, get_run_details.py.
#---------------------------------------------------------------------->
