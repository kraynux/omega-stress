from datetime import datetime, timezone

import pytest

from omega_stress.core.enums import ExportFormat, IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.reports.models import (
    ExportJob,
    ReportContent,
    ReportDiagnostic,
    ReportSummary,
)
from omega_stress.domain.runs.models import IntervalSample, LoadResult

STARTED = datetime(2026, 8, 24, 10, 0, tzinfo=timezone.utc)
FINISHED = datetime(2026, 8, 24, 10, 3, tzinfo=timezone.utc)


@pytest.fixture
def report_content() -> ReportContent:
    summary = ReportSummary(
        run_id="run-1",
        target_address="https://example.org/",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
        finished_at=FINISHED,
        duration_minutes=3.0,
    )
    result = LoadResult(
        verdict=RunVerdict.SUCCESS,
        requested_rate_per_minute=250,
        observed_rate_per_minute=248.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        total_requests=750,
    )
    diagnostic = ReportDiagnostic(
        verdict=RunVerdict.SUCCESS,
        headline="Le test s'est deroule normalement, sans depassement de seuil.",
        recommendations=(),
    )
    return ReportContent(summary=summary, result=result, diagnostic=diagnostic)


@pytest.fixture
def report_content_with_samples(report_content: ReportContent) -> ReportContent:
    samples = (
        IntervalSample(
            at_second=0.0,
            observed_rate_per_minute=240.0,
            p50_latency_ms=9.0,
            p95_latency_ms=18.0,
            p99_latency_ms=28.0,
            error_count=0,
            request_count=4,
        ),
        IntervalSample(
            at_second=1.0,
            observed_rate_per_minute=250.0,
            p50_latency_ms=11.0,
            p95_latency_ms=22.0,
            p99_latency_ms=32.0,
            error_count=1,
            request_count=4,
        ),
    )
    result = LoadResult(
        verdict=report_content.result.verdict,
        requested_rate_per_minute=report_content.result.requested_rate_per_minute,
        observed_rate_per_minute=report_content.result.observed_rate_per_minute,
        p50_latency_ms=report_content.result.p50_latency_ms,
        p95_latency_ms=report_content.result.p95_latency_ms,
        p99_latency_ms=report_content.result.p99_latency_ms,
        error_count=report_content.result.error_count,
        total_requests=report_content.result.total_requests,
        samples=samples,
    )
    return ReportContent(
        summary=report_content.summary, result=result, diagnostic=report_content.diagnostic
    )


def make_job(
    tmp_path, *, fmt: ExportFormat, filename: str, export_theme: str = "omega-base"
) -> ExportJob:
    return ExportJob(
        id="job-1",
        run_id="run-1",
        format=fmt,
        destination_path=str(tmp_path / filename),
        created_at=STARTED,
        export_theme=export_theme,
    )
