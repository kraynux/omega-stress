# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation SQLite du port RunRepository."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.runs.models import IntervalSample, LoadResult, LoadRun, RunEvent
from omega_stress.infrastructure.exceptions import StorageError


class SqliteRunRepository:
    """Implemente ports/run_repository.py::RunRepository. LoadResult est
    aplati directement sur les colonnes de `runs` (voir schema.py)."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, run: LoadRun) -> None:
        result = run.result
        try:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO runs (
                    id, profile_id, target_id, family, level, started_at, finished_at,
                    notes, is_precheck, verdict, requested_rate_per_minute,
                    observed_rate_per_minute, p50_latency_ms, p95_latency_ms,
                    p99_latency_ms, error_count, total_requests, events_json, samples_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.profile_id,
                    run.target_id,
                    run.family.value,
                    run.level.value,
                    run.started_at.isoformat(),
                    run.finished_at.isoformat() if run.finished_at is not None else None,
                    run.notes,
                    int(run.is_precheck),
                    result.verdict.value if result is not None else None,
                    result.requested_rate_per_minute if result is not None else None,
                    result.observed_rate_per_minute if result is not None else None,
                    result.p50_latency_ms if result is not None else None,
                    result.p95_latency_ms if result is not None else None,
                    result.p99_latency_ms if result is not None else None,
                    result.error_count if result is not None else None,
                    result.total_requests if result is not None else None,
                    _serialize_events(result.events) if result is not None else None,
                    _serialize_samples(result.samples) if result is not None else None,
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de sauvegarde du run {run.id!r} : {exc}") from exc

    def get(self, run_id: str) -> LoadRun | None:
        try:
            row = self._connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de lecture du run {run_id!r} : {exc}") from exc
        return _row_to_run(row) if row is not None else None

    def list_history(
        self,
        *,
        target_id: str | None = None,
        profile_id: str | None = None,
        limit: int = 50,
    ) -> tuple[LoadRun, ...]:
        query = "SELECT * FROM runs WHERE 1 = 1"
        params: list[object] = []
        if target_id is not None:
            query += " AND target_id = ?"
            params.append(target_id)
        if profile_id is not None:
            query += " AND profile_id = ?"
            params.append(profile_id)
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        try:
            rows = self._connection.execute(query, params).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de listage de l'historique des runs : {exc}") from exc
        return tuple(_row_to_run(row) for row in rows)

    def clear(self) -> None:
        try:
            self._connection.execute("DELETE FROM runs")
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Echec de purge de l'historique des runs : {exc}") from exc


def _serialize_events(events: tuple[RunEvent, ...]) -> str:
    return json.dumps(
        [
            {"occurred_at": e.occurred_at.isoformat(), "kind": e.kind, "message": e.message}
            for e in events
        ]
    )


def _deserialize_events(raw: str | None) -> tuple[RunEvent, ...]:
    if not raw:
        return ()
    return tuple(
        RunEvent(
            occurred_at=datetime.fromisoformat(item["occurred_at"]),
            kind=item["kind"],
            message=item["message"],
        )
        for item in json.loads(raw)
    )


def _serialize_samples(samples: tuple[IntervalSample, ...]) -> str:
    return json.dumps(
        [
            {
                "at_second": s.at_second,
                "observed_rate_per_minute": s.observed_rate_per_minute,
                "p50_latency_ms": s.p50_latency_ms,
                "p95_latency_ms": s.p95_latency_ms,
                "p99_latency_ms": s.p99_latency_ms,
                "error_count": s.error_count,
                "request_count": s.request_count,
            }
            for s in samples
        ]
    )


def _deserialize_samples(raw: str | None) -> tuple[IntervalSample, ...]:
    if not raw:
        return ()
    return tuple(IntervalSample(**item) for item in json.loads(raw))


def _row_to_run(row: sqlite3.Row) -> LoadRun:
    result: LoadResult | None = None
    if row["verdict"] is not None:
        result = LoadResult(
            verdict=RunVerdict(row["verdict"]),
            requested_rate_per_minute=row["requested_rate_per_minute"],
            observed_rate_per_minute=row["observed_rate_per_minute"],
            p50_latency_ms=row["p50_latency_ms"],
            p95_latency_ms=row["p95_latency_ms"],
            p99_latency_ms=row["p99_latency_ms"],
            error_count=row["error_count"],
            total_requests=row["total_requests"],
            events=_deserialize_events(row["events_json"]),
            samples=_deserialize_samples(row["samples_json"]),
        )

    return LoadRun(
        id=row["id"],
        profile_id=row["profile_id"],
        target_id=row["target_id"],
        family=TestFamily(row["family"]),
        level=IntensityLevel(row["level"]),
        started_at=datetime.fromisoformat(row["started_at"]),
        finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
        result=result,
        notes=row["notes"],
        is_precheck=bool(row["is_precheck"]),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Implementation concrete du port run_repository.py.
# Pourquoi dans infrastructure/storage/sqlite/ (charte) :
# - Adaptateur remplacable, traduit sqlite3.Error en StorageError.
# Ce qu'il ne contient PAS :
# - Aucune agregation de metriques (deja faite par
#   domain/runs/service.py::aggregate_samples() avant que save() ne soit
#   appele) : ce repository persiste un LoadResult deja construit, il ne
#   le calcule jamais.
# - Aucun filtre par date/type de test (voir ports/run_repository.py,
#   meme limitation documentee — construction dynamique de la requete
#   limitee a target_id/profile_id en V1).
# Points cles :
# - result est absent (verdict IS NULL) pour un run encore en cours :
#   _row_to_run() ne reconstruit un LoadResult que si verdict n'est pas
#   NULL, coherent avec l'invariant "finished_at et result presents
#   ensemble ou absents ensemble" de domain/runs/models.py.
# - events_json/samples_json (2026-08-24) : LoadResult.events/samples
#   serialises en JSON (liste de dicts plats), pas de table dediee — voir
#   schema.py pour la justification complete (volume borne par
#   construction). _deserialize_events()/_deserialize_samples() retombent
#   sur () pour une valeur NULL ou vide, jamais une erreur : une ligne
#   ecrite avant ce changement (colonnes NULL apres migration additive,
#   voir migrations.py) reste lisible sans exception.
# - list_history() construit sa requete dynamiquement (WHERE 1 = 1 comme
#   base neutre) pour ajouter les filtres optionnels sans dupliquer la
#   requete pour chaque combinaison de parametres.
# - clear() (2026-08-24) : DELETE FROM runs sans WHERE, purge complete et
#   irreversible (voir ports/run_repository.py).
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py (indirectement, via l'appelant qui
#   persiste le LoadRun retourne), application/queries/list_history.py,
#   get_run_details.py.
#---------------------------------------------------------------------->
