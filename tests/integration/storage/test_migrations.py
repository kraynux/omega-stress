from omega_stress.infrastructure.storage.sqlite.migrations import apply_schema


def _column_names(connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}


def test_apply_schema_creates_expected_tables(sqlite_connection):
    tables = {
        row[0]
        for row in sqlite_connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }

    assert {"targets", "pinned_targets", "profiles", "runs", "export_jobs"} <= tables


def test_apply_schema_is_idempotent(sqlite_connection):
    apply_schema(sqlite_connection)
    apply_schema(sqlite_connection)

    assert "events_json" in _column_names(sqlite_connection, "runs")


def test_additive_columns_are_added_to_a_pre_existing_table(tmp_path):
    """Reproduit une base creee AVANT l'ajout de events_json/samples_json
    a schema.py : `runs` existe deja, sans ces deux colonnes. apply_schema()
    doit les ajouter plutot que de les ignorer silencieusement (CREATE
    TABLE IF NOT EXISTS seul ne le ferait jamais)."""
    import sqlite3

    connection = sqlite3.connect(tmp_path / "legacy.db")
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE runs (
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
            total_requests INTEGER
        )
        """
    )
    connection.commit()
    assert "events_json" not in _column_names(connection, "runs")

    apply_schema(connection)

    columns = _column_names(connection, "runs")
    assert "events_json" in columns
    assert "samples_json" in columns
    connection.close()
