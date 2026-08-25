# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation SQLite du port TargetRepository."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from omega_stress.infrastructure.exceptions import StorageError


class SqliteTargetRepository:
    """Implemente ports/target_repository.py::TargetRepository. Deux
    tables independantes (targets, pinned_targets), voir schema.py pour
    la justification de la denormalisation."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save_recent(self, target: Target) -> None:
        try:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO targets (
                    id, scheme, host, port, path, tags, notes, created_at, last_used_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _target_params(target),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de sauvegarde de la cible {target.id!r} : {exc}") from exc

    def save_pinned(self, pinned: PinnedTarget) -> None:
        try:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO pinned_targets (
                    id, scheme, host, port, path, tags, notes, created_at, last_used_at,
                    pinned_at, authorized_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *_target_params(pinned.target),
                    pinned.pinned_at.isoformat(),
                    pinned.authorized_at.isoformat(),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(
                f"Echec d'epinglage de la cible {pinned.target.id!r} : {exc}"
            ) from exc

    def get(self, target_id: str) -> Target | None:
        try:
            row = self._connection.execute(
                "SELECT * FROM pinned_targets WHERE id = ?", (target_id,)
            ).fetchone()
            if row is None:
                row = self._connection.execute(
                    "SELECT * FROM targets WHERE id = ?", (target_id,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de lecture de la cible {target_id!r} : {exc}") from exc
        return _row_to_target(row) if row is not None else None

    def get_pinned(self, target_id: str) -> PinnedTarget | None:
        try:
            row = self._connection.execute(
                "SELECT * FROM pinned_targets WHERE id = ?", (target_id,)
            ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(
                f"Echec de lecture de la cible epinglee {target_id!r} : {exc}"
            ) from exc
        return _row_to_pinned_target(row) if row is not None else None

    def list_pinned(self) -> tuple[PinnedTarget, ...]:
        try:
            rows = self._connection.execute(
                "SELECT * FROM pinned_targets ORDER BY pinned_at DESC"
            ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de listage des cibles epinglees : {exc}") from exc
        return tuple(_row_to_pinned_target(row) for row in rows)

    def list_recent(self, *, limit: int = 10) -> tuple[Target, ...]:
        try:
            rows = self._connection.execute(
                "SELECT * FROM targets ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de listage des cibles recentes : {exc}") from exc
        return tuple(_row_to_target(row) for row in rows)

    def unpin(self, target_id: str) -> None:
        try:
            self._connection.execute("DELETE FROM pinned_targets WHERE id = ?", (target_id,))
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de desepinglage de la cible {target_id!r} : {exc}") from exc

    def clear_recent(self) -> None:
        try:
            self._connection.execute("DELETE FROM targets")
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de purge des cibles recentes : {exc}") from exc

    def clear_all(self) -> None:
        try:
            self._connection.execute("DELETE FROM targets")
            self._connection.execute("DELETE FROM pinned_targets")
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de purge de toutes les cibles : {exc}") from exc


def _target_params(target: Target) -> tuple[object, ...]:
    return (
        target.id,
        target.address.scheme,
        target.address.host,
        target.address.port,
        target.address.path,
        json.dumps(list(target.tags)),
        target.notes,
        target.created_at.isoformat(),
        target.last_used_at.isoformat() if target.last_used_at is not None else None,
    )


def _row_to_target(row: sqlite3.Row) -> Target:
    return Target(
        id=row["id"],
        address=TargetAddress(
            scheme=row["scheme"], host=row["host"], port=row["port"], path=row["path"]
        ),
        created_at=datetime.fromisoformat(row["created_at"]),
        tags=tuple(json.loads(row["tags"])),
        notes=row["notes"],
        last_used_at=datetime.fromisoformat(row["last_used_at"]) if row["last_used_at"] else None,
    )


def _row_to_pinned_target(row: sqlite3.Row) -> PinnedTarget:
    return PinnedTarget(
        target=_row_to_target(row),
        pinned_at=datetime.fromisoformat(row["pinned_at"]),
        authorized_at=datetime.fromisoformat(row["authorized_at"]),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Implementation concrete du port target_repository.py, sur les deux
#   tables independantes targets/pinned_targets (voir schema.py).
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Adaptateur remplacable, traduit toutes les sqlite3.Error en
#   StorageError.
# Ce qu'il ne contient PAS :
# - Aucune regle d'autorisation (deja actee par
#   domain/targets/service.py::pin() avant que save_pinned() ne soit
#   appele).
# Points cles :
# - get() cherche d'abord dans pinned_targets, puis dans targets : une
#   cible epinglee reste resolvable par get() meme si elle n'a jamais ete
#   ajoutee via save_recent() (coherent avec le fait que les deux tables
#   sont indexees par le meme id, mais alimentees independamment).
# - _target_params() est une fonction de mapping partagee par
#   save_recent() et save_pinned() (les deux tables ont les memes
#   colonnes d'adresse) : evite de dupliquer neuf champs deux fois.
# - list_recent() ne filtre pas les cibles deja epinglees : la
#   deduplication reste du ressort de
#   application/queries/list_targets.py (voir son propre commentaire
#   INFO DEV), pas de ce repository.
# - clear_recent()/clear_all() (2026-08-24) : deux DELETE simples, sans
#   WHERE (voir ports/target_repository.py pour la portee exacte de
#   chacune) — clear_all() efface les deux tables dans le meme commit,
#   jamais l'une sans l'autre en cas d'echec partiel.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py cree une instance unique.
#---------------------------------------------------------------------->
