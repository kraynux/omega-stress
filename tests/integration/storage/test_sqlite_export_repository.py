from datetime import datetime, timezone

from omega_stress.core.enums import ExportFormat
from omega_stress.domain.reports.models import ExportJob
from omega_stress.infrastructure.storage.sqlite.export_repository import (
    SqliteExportRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _job(job_id: str = "job-1", run_id: str = "run-1", **overrides) -> ExportJob:
    defaults = dict(
        id=job_id,
        run_id=run_id,
        format=ExportFormat.HTML,
        destination_path="/tmp/report.html",
        created_at=NOW,
        export_theme="omega-neon",
    )
    defaults.update(overrides)
    return ExportJob(**defaults)


def test_save_and_list_for_run_roundtrip(sqlite_connection):
    repo = SqliteExportRepository(sqlite_connection)
    job = _job()

    repo.save(job)
    fetched = repo.list_for_run("run-1")

    assert fetched == (job,)


def test_list_for_run_filters_by_run(sqlite_connection):
    repo = SqliteExportRepository(sqlite_connection)
    repo.save(_job("job-1", run_id="run-1"))
    repo.save(_job("job-2", run_id="run-2"))

    assert {j.id for j in repo.list_for_run("run-1")} == {"job-1"}


def test_list_for_run_returns_empty_tuple_when_none_found(sqlite_connection):
    repo = SqliteExportRepository(sqlite_connection)

    assert repo.list_for_run("does-not-exist") == ()
