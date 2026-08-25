# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Application du schema SQLite sur une connexion ouverte."""
from __future__ import annotations

import sqlite3

from omega_stress.infrastructure.exceptions import StorageError
from omega_stress.infrastructure.storage.sqlite.schema import ADDITIVE_COLUMNS, SCHEMA_STATEMENTS


def apply_schema(connection: sqlite3.Connection) -> None:
    """Cree les tables manquantes puis ajoute les colonnes additives
    manquantes sur les tables existantes. Idempotent : peut etre appele a
    chaque demarrage sans effet sur une base deja a jour."""
    try:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        _ensure_additive_columns(connection)
        connection.commit()
    except sqlite3.Error as exc:
        raise StorageError(f"Echec de l'initialisation du schema SQLite : {exc}") from exc


def _ensure_additive_columns(connection: sqlite3.Connection) -> None:
    """Ajoute chaque colonne de schema.py::ADDITIVE_COLUMNS absente de sa
    table (verifie via PRAGMA table_info, pas de try/except sur un
    "duplicate column" qui masquerait une vraie erreur SQL par ailleurs).
    Ne fait rien sur une table qui a deja la colonne (base initialisee
    apres l'ajout de cette colonne a SCHEMA_STATEMENTS, ou deja migree par
    un appel precedent)."""
    # Interpolation directe de table/colonne/type sans risque : les trois
    # valeurs viennent exclusivement de schema.py::ADDITIVE_COLUMNS (une
    # constante fixee dans le code), jamais d'une entree utilisateur — et
    # SQLite ne permet de toute facon pas de parametrer un identifiant via
    # "?" (seulement des valeurs), seule la syntaxe DDL brute fonctionne ici.
    for table, column, sql_type in ADDITIVE_COLUMNS:
        existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        if column not in existing:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Applique le DDL de schema.py sur une connexion deja ouverte.
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Detail d'infrastructure pur : orchestre sqlite3, traduit ses erreurs
#   en StorageError avant qu'elles ne remontent plus loin (ARCHITECTURE.md
#   §5.3).
# Ce qu'il ne contient PAS :
# - Toujours aucune migration versionnee au sens strict (pas de table
#   schema_version, pas de scripts numerotes) : _ensure_additive_columns()
#   (2026-08-24) est le strict minimum pour le premier cas reel rencontre
#   (deux colonnes ajoutees a `runs`), pas un vrai systeme generique — il
#   ne sait qu'AJOUTER une colonne nullable a une table existante, jamais
#   la renommer, la retyper, ni supprimer/modifier une table. Le
#   commentaire precedent de ce fichier annoncait ce moment ("necessaire
#   des la premiere evolution de schema apres une version publiee") : ce
#   projet n'a encore rien publie, d'ou un mecanisme delibérement minimal
#   plutot qu'un vrai framework de migrations — a agrandir seulement
#   quand un futur changement depasse "ajouter une colonne".
# Points cles :
# - _ensure_additive_columns() s'appuie sur PRAGMA table_info() (jamais un
#   try/except sur "duplicate column name", qui masquerait silencieusement
#   une autre erreur SQL sans rapport) : verifie explicitement l'etat
#   avant d'agir, idempotent par construction plutot que par rattrapage
#   d'exception.
# - apply_schema() ne fait pas de rollback partiel en cas d'echec au
#   milieu de la liste : SQLite execute chaque CREATE TABLE
#   independamment, un echec sur l'une n'annule pas les precedentes deja
#   commises... en realite ici aucun commit() n'a lieu avant la fin de la
#   boucle, donc un echec en cours de route ne laisse aucune table
#   creee par CET appel (mais les tables deja existantes d'un appel
#   precedent reussi restent, ce qui est le comportement voulu pour
#   l'idempotence).
# Comment il sera utilise (apercu) :
# - app/bootstrap.py appelle apply_schema() juste apres
#   connection.py::open_connection().
#---------------------------------------------------------------------->
