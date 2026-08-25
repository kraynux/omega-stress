from datetime import datetime, timezone

from omega_stress.core.enums import ExportFormat, IntensityLevel, TestFamily
from omega_stress.domain.reports.models import ExportJob, ReportSummary
from omega_stress.infrastructure.exporters.destination_resolver import resolve_destination_file

CREATED = datetime(2026, 8, 24, tzinfo=timezone.utc)
STARTED = datetime(2026, 8, 24, 10, 0, 0, tzinfo=timezone.utc)


def _job(destination_path: str) -> ExportJob:
    return ExportJob(
        id="job-1",
        run_id="run-1",
        format=ExportFormat.JSON,
        destination_path=destination_path,
        created_at=CREATED,
    )


def _summary(family: TestFamily = TestFamily.REQUEST) -> ReportSummary:
    return ReportSummary(
        run_id="run-1",
        target_address="https://example.org/",
        family=family,
        level=IntensityLevel.BAS,
        started_at=STARTED,
        finished_at=STARTED,
        duration_minutes=1.0,
    )


def test_existing_directory_gets_a_derived_filename(tmp_path):
    job = _job(str(tmp_path))

    resolved = resolve_destination_file(job, _summary(), extension="json")

    assert resolved == tmp_path / "test-requetes-20260824-100000.json"


def test_derived_filename_reflects_the_test_family(tmp_path):
    job = _job(str(tmp_path))

    resolved = resolve_destination_file(job, _summary(TestFamily.RAMP), extension="json")

    assert resolved == tmp_path / "test-charge-20260824-100000.json"


def test_trailing_separator_is_treated_as_a_folder_even_if_not_created_yet(tmp_path):
    not_yet_created = tmp_path / "exports"
    job = _job(f"{not_yet_created}/")

    resolved = resolve_destination_file(job, _summary(TestFamily.CONNECTION), extension="html")

    assert resolved == not_yet_created / "test-connexions-20260824-100000.html"


def test_explicit_file_path_is_kept_as_is(tmp_path):
    explicit = tmp_path / "mon-rapport.csv"
    job = _job(str(explicit))

    resolved = resolve_destination_file(job, _summary(), extension="csv")

    assert resolved == explicit
