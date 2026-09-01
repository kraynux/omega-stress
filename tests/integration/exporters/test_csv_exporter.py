import csv

from omega_stress.core.enums import ExportFormat
from omega_stress.infrastructure.exporters.csv_exporter import CsvReportExporter

from .conftest import make_job


def test_export_writes_header_and_one_data_row(tmp_path, report_content):
    job = make_job(tmp_path, fmt=ExportFormat.CSV, filename="report.csv")
    exporter = CsvReportExporter()

    written_path = exporter.export(report_content, job)

    with open(written_path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["run_id"] == "run-1"
    assert rows[0]["verdict"] == "success"
    assert rows[0]["error_count"] == "0"
    assert rows[0]["errors_timeout"] == "0"
    assert rows[0]["safety_mode"] == "True"


def test_export_includes_error_breakdown_and_peak_system_columns(
    tmp_path, report_content_with_samples
):
    job = make_job(tmp_path, fmt=ExportFormat.CSV, filename="report.csv")
    exporter = CsvReportExporter()

    written_path = exporter.export(report_content_with_samples, job)

    with open(written_path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1  # toujours une ligne par run, pas une par intervalle
    assert rows[0]["errors_http_5xx"] == "1"
    assert rows[0]["peak_cpu_percent_generator"] == "22.0"
    assert rows[0]["peak_memory_rss_mb"] == "64.0"


def test_export_to_an_existing_folder_derives_a_filename_instead_of_crashing(
    tmp_path, report_content
):
    job = make_job(tmp_path, fmt=ExportFormat.CSV, filename="")
    exporter = CsvReportExporter()

    written_path = exporter.export(report_content, job)

    assert written_path == str(tmp_path / "test-requetes-20260824-100000.csv")


def test_export_stays_one_row_and_joins_recommendations(tmp_path, report_content):
    from dataclasses import replace

    content = replace(
        report_content,
        diagnostic=replace(
            report_content.diagnostic, recommendations=("cible lente", "goulot local")
        ),
    )
    job = make_job(tmp_path, fmt=ExportFormat.CSV, filename="report.csv")
    exporter = CsvReportExporter()

    written_path = exporter.export(content, job)

    with open(written_path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["diagnostic_recommendations"] == "cible lente; goulot local"
