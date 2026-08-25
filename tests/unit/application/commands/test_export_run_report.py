from datetime import datetime, timezone

from omega_stress.application.commands.export_run_report import export_run_report
from omega_stress.application.dto.export_dto import ExportRequestDTO
from omega_stress.core.enums import ExportFormat, IntensityLevel, RunVerdict, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import LoadResult, LoadRun
from omega_stress.domain.targets.models import Target, TargetAddress
from tests.fixtures.fakes import (
    FakeExportRepository,
    FakeReportExporter,
    FakeRunRepository,
    FakeTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _finished_run() -> LoadRun:
    return LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=NOW,
        finished_at=NOW,
        result=LoadResult(
            verdict=RunVerdict.SUCCESS,
            requested_rate_per_minute=250,
            observed_rate_per_minute=248.0,
            p50_latency_ms=10.0,
            p95_latency_ms=20.0,
            p99_latency_ms=30.0,
            error_count=0,
            total_requests=250,
        ),
    )


async def test_export_writes_via_matching_format_exporter():
    run_repository = FakeRunRepository()
    run_repository.save(_finished_run())
    target_repository = FakeTargetRepository()
    target_repository.save_recent(
        Target(id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW)
    )
    export_repository = FakeExportRepository()
    json_exporter = FakeReportExporter("/tmp/report.json")
    html_exporter = FakeReportExporter("/tmp/report.html")

    result = await export_run_report(
        ExportRequestDTO(run_id="run-1", format="json", destination_path="/tmp/report.json"),
        run_repository=run_repository,
        target_repository=target_repository,
        export_repository=export_repository,
        exporters={ExportFormat.JSON: json_exporter, ExportFormat.HTML: html_exporter},
        id_factory=lambda: "job-1",
        now=NOW,
    )

    assert isinstance(result, Ok)
    assert result.value.written_path == "/tmp/report.json"
    assert len(json_exporter.exported) == 1
    assert len(html_exporter.exported) == 0
    assert len(export_repository.list_for_run("run-1")) == 1


async def test_export_rejects_unfinished_run():
    run_repository = FakeRunRepository()
    run_repository.save(
        LoadRun(
            id="run-1",
            profile_id=None,
            target_id="t-1",
            family=TestFamily.REQUEST,
            level=IntensityLevel.BAS,
            started_at=NOW,
        )
    )

    result = await export_run_report(
        ExportRequestDTO(run_id="run-1", format="json", destination_path="/tmp/report.json"),
        run_repository=run_repository,
        target_repository=FakeTargetRepository(),
        export_repository=FakeExportRepository(),
        exporters={},
        id_factory=lambda: "job-1",
        now=NOW,
    )

    assert isinstance(result, Err)


async def test_export_rejects_unknown_run():
    result = await export_run_report(
        ExportRequestDTO(run_id="does-not-exist", format="json", destination_path="/tmp/x.json"),
        run_repository=FakeRunRepository(),
        target_repository=FakeTargetRepository(),
        export_repository=FakeExportRepository(),
        exporters={},
        id_factory=lambda: "job-1",
        now=NOW,
    )

    assert isinstance(result, Err)


async def test_export_rejects_html_with_unknown_theme():
    run_repository = FakeRunRepository()
    run_repository.save(_finished_run())

    result = await export_run_report(
        ExportRequestDTO(
            run_id="run-1",
            format="html",
            destination_path="/tmp/report.html",
            export_theme="does-not-exist",
        ),
        run_repository=run_repository,
        target_repository=FakeTargetRepository(),
        export_repository=FakeExportRepository(),
        exporters={ExportFormat.HTML: FakeReportExporter()},
        id_factory=lambda: "job-1",
        now=NOW,
    )

    assert isinstance(result, Err)
