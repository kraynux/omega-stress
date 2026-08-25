# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ouverture d'une connexion SQLite configuree pour le projet."""
from __future__ import annotations

import sqlite3
from pathlib import Path


def open_connection(path: Path) -> sqlite3.Connection:
    """Ouvre (et cree si besoin) la base SQLite au chemin donne, avec les
    pragmas necessaires a l'usage du projet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique pour ouvrir une connexion SQLite dans le
#   projet, avec sa configuration standard (row_factory, foreign_keys).
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Seul sous-paquet du projet ou `sqlite3` est importe (verifie par le
#   contrat import-linter "sqlite3 seulement dans
#   infrastructure.storage.sqlite", voir pyproject.toml).
# Ce qu'il ne contient PAS :
# - Aucune creation de table (voir schema.py/migrations.py, appeles
#   separement une fois la connexion ouverte).
# - Aucune traduction d'exception : sqlite3.Error peut remonter brut
#   depuis open_connection() (ex. permissions insuffisantes) — c'est
#   l'appelant immediat (app/bootstrap.py) qui doit decider de la
#   traduire en AdapterConfigurationError si besoin ; les repositories,
#   eux, catchent sqlite3.Error sur leurs PROPRES operations (voir
#   profile_repository.py etc.), pas sur l'ouverture de connexion.
# Points cles :
# - row_factory = sqlite3.Row : permet un acces par nom de colonne
#   (row["id"]) dans les repositories, plus lisible qu'un tuple positionnel.
# - PRAGMA foreign_keys = ON : necessaire a chaque connexion (SQLite ne
#   l'active pas par defaut), pour que la reference
#   pinned_targets.target_id -> targets.id soit reellement contrainte.
# Comment il sera utilise (apercu) :
# - app/bootstrap.py appelle open_connection(paths.db_path()) une fois au
#   demarrage, partage ensuite entre tous les repositories SQLite.
#---------------------------------------------------------------------->
