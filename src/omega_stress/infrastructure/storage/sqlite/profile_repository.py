# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation SQLite du port ProfileRepository."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.infrastructure.exceptions import StorageError


class SqliteProfileRepository:
    """Implemente ports/profile_repository.py::ProfileRepository. Classe
    concrete prefixee par sa techno (charte, §3) car elle partage son nom
    de module avec le port qu'elle implemente."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, profile: Profile) -> None:
        try:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO profiles (
                    id, name, description, default_target_id, family, level,
                    duration_minutes, max_error_rate, max_p95_latency_ms, tags,
                    extended_duration_authorized, frozen, frozen_at, favorite,
                    archived, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.id,
                    profile.name,
                    profile.description,
                    profile.default_target_id,
                    profile.family.value,
                    profile.level.value,
                    profile.duration.minutes,
                    profile.thresholds.max_error_rate,
                    profile.thresholds.max_p95_latency_ms,
                    json.dumps(list(profile.tags)),
                    int(profile.extended_duration_authorized),
                    int(profile.frozen),
                    profile.frozen_at.isoformat() if profile.frozen_at is not None else None,
                    int(profile.favorite),
                    int(profile.archived),
                    profile.created_at.isoformat(),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de sauvegarde du profil {profile.id!r} : {exc}") from exc

    def get(self, profile_id: str) -> Profile | None:
        try:
            row = self._connection.execute(
                "SELECT * FROM profiles WHERE id = ?", (profile_id,)
            ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de lecture du profil {profile_id!r} : {exc}") from exc
        return _row_to_profile(row) if row is not None else None

    def list_all(self) -> tuple[Profile, ...]:
        try:
            rows = self._connection.execute("SELECT * FROM profiles").fetchall()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de listage des profils : {exc}") from exc
        return tuple(_row_to_profile(row) for row in rows)

    def delete(self, profile_id: str) -> None:
        try:
            self._connection.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de suppression du profil {profile_id!r} : {exc}") from exc


def _row_to_profile(row: sqlite3.Row) -> Profile:
    return Profile(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        default_target_id=row["default_target_id"],
        family=TestFamily(row["family"]),
        level=IntensityLevel(row["level"]),
        duration=Duration(minutes=row["duration_minutes"]),
        thresholds=Thresholds(
            max_error_rate=row["max_error_rate"], max_p95_latency_ms=row["max_p95_latency_ms"]
        ),
        created_at=datetime.fromisoformat(row["created_at"]),
        tags=tuple(json.loads(row["tags"])),
        extended_duration_authorized=bool(row["extended_duration_authorized"]),
        frozen=bool(row["frozen"]),
        frozen_at=datetime.fromisoformat(row["frozen_at"]) if row["frozen_at"] else None,
        favorite=bool(row["favorite"]),
        archived=bool(row["archived"]),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Implementation concrete du port profile_repository.py, seule classe
#   du projet a traduire un Profile en lignes SQLite et inversement.
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Adaptateur remplacable : toute autre implementation du meme Protocol
#   (ex. en memoire, fichier JSON) fonctionnerait a l'identique cote
#   application/, sans aucun changement.
# Ce qu'il ne contient PAS :
# - Aucune regle metier (validation deja faite en amont par
#   domain/profiles/validation.py avant que save() ne soit appele).
# - Aucune exception sqlite3.Error qui remonte brute : toutes traduites
#   en StorageError (ARCHITECTURE.md §5.3).
# Points cles :
# - save() utilise INSERT OR REPLACE : upsert simple par cle primaire,
#   suffisant tant qu'aucune contrainte de FK n'y reference `profiles`
#   (contrairement a targets/pinned_targets).
# - _row_to_profile() est une fonction module-level privee (pas une
#   methode) : pure fonction de mapping, testable isolement si besoin,
#   sans instance de repository.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py cree une instance unique, injectee dans
#   les commands/queries de application/ via le port.
#---------------------------------------------------------------------->
