# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Definition DDL des tables SQLite du projet."""
from __future__ import annotations

SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS targets (
        id TEXT PRIMARY KEY,
        scheme TEXT NOT NULL,
        host TEXT NOT NULL,
        port INTEGER,
        path TEXT NOT NULL,
        tags TEXT NOT NULL,
        notes TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_used_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pinned_targets (
        id TEXT PRIMARY KEY,
        scheme TEXT NOT NULL,
        host TEXT NOT NULL,
        port INTEGER,
        path TEXT NOT NULL,
        tags TEXT NOT NULL,
        notes TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_used_at TEXT,
        pinned_at TEXT NOT NULL,
        authorized_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        default_target_id TEXT NOT NULL,
        family TEXT NOT NULL,
        level TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        max_error_rate REAL NOT NULL,
        max_p95_latency_ms REAL,
        tags TEXT NOT NULL,
        extended_duration_authorized INTEGER NOT NULL,
        frozen INTEGER NOT NULL,
        frozen_at TEXT,
        favorite INTEGER NOT NULL,
        archived INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        profile_id TEXT,
        target_id TEXT NOT NULL,
        family TEXT NOT NULL,
        level TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        notes TEXT NOT NULL,
        is_precheck INTEGER NOT NULL,
        verdict TEXT,
        requested_rate_per_minute INTEGER,
        observed_rate_per_minute REAL,
        p50_latency_ms REAL,
        p95_latency_ms REAL,
        p99_latency_ms REAL,
        error_count INTEGER,
        total_requests INTEGER,
        events_json TEXT,
        samples_json TEXT,
        errors_json TEXT,
        peak_cpu_percent_generator REAL,
        peak_memory_rss_mb REAL,
        duration_preset_id TEXT,
        safety_mode INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS export_jobs (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        format TEXT NOT NULL,
        destination_path TEXT NOT NULL,
        export_theme TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
)

ADDITIVE_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("runs", "events_json", "TEXT"),
    ("runs", "samples_json", "TEXT"),
    ("runs", "errors_json", "TEXT"),
    ("runs", "peak_cpu_percent_generator", "REAL"),
    ("runs", "peak_memory_rss_mb", "REAL"),
    ("runs", "duration_preset_id", "TEXT"),
    ("runs", "safety_mode", "INTEGER"),
)
"""Colonnes ajoutees a une table EXISTANTE apres sa premiere creation
(table, colonne, type SQL) — voir migrations.py::_ensure_additive_columns().
`CREATE TABLE IF NOT EXISTS` ne retouche jamais une table deja creee : une
base initialisee avant l'ajout de ces colonnes ne les gagnerait jamais
sans ce mecanisme separe. errors_json/peak_cpu_percent_generator/
peak_memory_rss_mb (Phase 1 observabilite), duration_preset_id (mode
"profil" D1-D6), safety_mode ("mode securite" a cocher) suivent le meme
motif que events_json/samples_json : ajoutees ici ET dans le CREATE
TABLE ci-dessus pour couvrir les deux cas (base neuve vs base existante
a migrer). safety_mode nullable (pas de DEFAULT) : une base migree lit
NULL pour tout run historique, relu comme True (voir run_repository.py)
— ces runs antérieurs tournaient TOUJOURS avec les garde-fous actifs,
avant que ce champ n'existe."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte le DDL de toutes les tables du projet, sous forme de tuple de
#   requetes CREATE TABLE IF NOT EXISTS idempotentes.
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Detail concret du schema de stockage, jamais une politique de
#   domaine (aucune valeur de seuil/duree/intensite ici, uniquement de la
#   structure de table).
# Ce qu'il ne contient PAS :
# - Aucune execution (voir migrations.py, qui applique ces requetes sur
#   une connexion).
# - Aucun index explicite en V1 (le volume attendu — usage local
#   mono-utilisateur, historique borne — ne justifie pas encore
#   d'optimisation ; a ajouter si un besoin de performance reel apparait).
# Points cles :
# - LoadResult est aplati directement sur la table runs (verdict,
#   requested_rate_per_minute, ...) plutot que dans une table separee :
#   relation 1-1 stricte avec un run, pas de justification a une jointure
#   supplementaire en V1.
# - RunEvent/IntervalSample n'ont pas de table dediee : serialises en
#   JSON dans runs.events_json/samples_json (colonnes ajoutees le
#   2026-08-24, meme precedent de denormalisation que `tags` ci-dessous)
#   plutot qu'une table par ligne — volume borne par construction : au
#   plus quelques centaines de samples en mode manuel (5 min maximum,
#   domain/load/policies.py::allowed_durations_minutes()), jusqu'a ~7200
#   en mode "profil" D1-D6 (domain/load/duration_presets.py, profil
#   `soak` 120 min) — colonne TEXT libre sans limite pratique dans les
#   deux cas (voir aussi infrastructure/exporters/time_series_chart.py
#   pour le sous-echantillonnage cote graphique HTML). Pas de besoin de
#   requetage individuel sur un intervalle precis en V1.
# - tags (Profile, Target) est serialise en JSON dans une colonne TEXT :
#   pas de table de jointure profiles_tags/targets_tags, le volume et les
#   besoins de requetage sur les tags ne le justifient pas en V1.
# - pinned_targets duplique volontairement les colonnes d'adresse de
#   targets plutot que de referencer targets(id) par FK : correspond
#   exactement au modele du port (ports/target_repository.py), ou une
#   PinnedTarget est un instantane AUTONOME (elle embarque son propre
#   Target complet), pas un simple indicateur sur une cible existante —
#   une cible peut etre "recente" sans etre epinglee et inversement, les
#   deux listes sont independantes (voir
#   infrastructure/storage/sqlite/target_repository.py). Denormalisation
#   assumee : le volume attendu (poste local mono-utilisateur) ne
#   justifie pas la complexite d'une jointure pour ce gain marginal.
# - ADDITIVE_COLUMNS (2026-08-24) : liste separee de SCHEMA_STATEMENTS
#   expres, pas fusionnee dans le CREATE TABLE de `runs` — editer le
#   CREATE TABLE n'aurait aucun effet sur une base deja initialisee
#   (CREATE TABLE IF NOT EXISTS est un no-op des que la table existe).
#   Voir migrations.py pour le mecanisme qui l'applique reellement.
# Comment il sera utilise (apercu) :
# - infrastructure/storage/sqlite/migrations.py::apply_schema().
#---------------------------------------------------------------------->
