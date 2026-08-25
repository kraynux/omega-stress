from datetime import datetime, timezone

from omega_stress.core.enums import ExportFormat
from omega_stress.core.results import Err, Ok
from omega_stress.domain.reports.models import ExportJob
from omega_stress.domain.reports.service import requires_theme, validate_export_job

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def test_requires_theme_true_only_for_html():
    assert requires_theme(ExportFormat.HTML) is True
    assert requires_theme(ExportFormat.JSON) is False
    assert requires_theme(ExportFormat.CSV) is False


def test_html_job_with_known_theme_is_valid():
    job = ExportJob(
        id="job-1",
        run_id="run-1",
        format=ExportFormat.HTML,
        destination_path="/tmp/report.html",
        created_at=NOW,
        export_theme="omega-neon",
    )

    assert isinstance(validate_export_job(job), Ok)


def test_html_job_with_unknown_theme_is_rejected():
    job = ExportJob(
        id="job-1",
        run_id="run-1",
        format=ExportFormat.HTML,
        destination_path="/tmp/report.html",
        created_at=NOW,
        export_theme="does-not-exist",
    )

    assert isinstance(validate_export_job(job), Err)


def test_json_job_ignores_theme_value():
    job = ExportJob(
        id="job-1",
        run_id="run-1",
        format=ExportFormat.JSON,
        destination_path="/tmp/report.json",
        created_at=NOW,
        export_theme="does-not-exist",
    )

    assert isinstance(validate_export_job(job), Ok)
