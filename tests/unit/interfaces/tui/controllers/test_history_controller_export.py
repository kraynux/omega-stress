from datetime import datetime, timezone

from omega_stress.core.enums import ExportFormat, IntensityLevel, RunVerdict, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import LoadResult, LoadRun
from omega_stress.interfaces.tui.controllers.history_controller import export_report
from tests.fixtures.fakes import (
    FakeExportRepository,
    FakeReportExporter,
    FakeRunRepository,
    FakeTargetRepository,
)


def _finished_run() -> LoadRun:
    return LoadRun(
        id="run-1",
        profile_id=None,
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=datetime(2026, 8, 24, tzinfo=timezone.utc),
        finished_at=datetime(2026, 8, 24, 0, 1, tzinfo=timezone.utc),
        result=LoadResult(
            verdict=RunVerdict.SUCCESS,
            requested_rate_per_minute=100,
            observed_rate_per_minute=98.0,
            p50_latency_ms=10.0,
            p95_latency_ms=20.0,
            p99_latency_ms=30.0,
            error_count=0,
            total_requests=98,
        ),
    )


async def test_export_report_writes_and_returns_result():
    run_repository = FakeRunRepository()
    run_repository.save(_finished_run())
    exporter = FakeReportExporter("/tmp/report.json")

    result = await export_report(
        "run-1",
        export_format=ExportFormat.JSON,
        destination_path="/tmp",
        export_theme="omega-base",
        run_repository=run_repository,
        target_repository=FakeTargetRepository(),
        export_repository=FakeExportRepository(),
        exporters={ExportFormat.JSON: exporter},
    )

    assert isinstance(result, Ok)
    assert result.value.written_path == "/tmp/report.json"
    assert len(exporter.exported) == 1


async def test_export_report_unknown_run_returns_err():
    result = await export_report(
        "unknown-run",
        export_format=ExportFormat.JSON,
        destination_path="/tmp",
        export_theme="omega-base",
        run_repository=FakeRunRepository(),
        target_repository=FakeTargetRepository(),
        export_repository=FakeExportRepository(),
        exporters={ExportFormat.JSON: FakeReportExporter()},
    )

    assert isinstance(result, Err)
