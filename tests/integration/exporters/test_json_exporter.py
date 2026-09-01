import json

from omega_stress.core.enums import ExportFormat
from omega_stress.infrastructure.exporters.json_exporter import JsonReportExporter

from .conftest import make_job


def test_export_writes_valid_json(tmp_path, report_content):
    job = make_job(tmp_path, fmt=ExportFormat.JSON, filename="report.json")
    exporter = JsonReportExporter()

    written_path = exporter.export(report_content, job)

    with open(written_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["summary"]["run_id"] == "run-1"
    assert payload["result"]["verdict"] == "success"
    assert payload["diagnostic"]["recommendations"] == []
    assert payload["summary"]["safety_mode"] is True


def test_export_creates_parent_directories(tmp_path, report_content):
    job = make_job(tmp_path, fmt=ExportFormat.JSON, filename="nested/report.json")
    exporter = JsonReportExporter()

    written_path = exporter.export(report_content, job)

    assert (tmp_path / "nested" / "report.json").exists()
    assert written_path.endswith("report.json")


def test_export_to_an_existing_folder_derives_a_filename_instead_of_crashing(
    tmp_path, report_content
):
    job = make_job(tmp_path, fmt=ExportFormat.JSON, filename="")
    exporter = JsonReportExporter()

    written_path = exporter.export(report_content, job)

    assert written_path == str(tmp_path / "test-requetes-20260824-100000.json")


def test_export_includes_the_full_sample_history(tmp_path, report_content_with_samples):
    job = make_job(tmp_path, fmt=ExportFormat.JSON, filename="report.json")
    exporter = JsonReportExporter()

    written_path = exporter.export(report_content_with_samples, job)

    with open(written_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    samples = payload["result"]["samples"]
    assert len(samples) == 2
    assert samples[0]["at_second"] == 0.0
    assert samples[1]["error_count"] == 1


def test_export_includes_error_breakdown_and_peak_system_metrics(
    tmp_path, report_content_with_samples
):
    job = make_job(tmp_path, fmt=ExportFormat.JSON, filename="report.json")
    exporter = JsonReportExporter()

    written_path = exporter.export(report_content_with_samples, job)

    with open(written_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["result"]["errors"] == {
        "timeout": 0,
        "connection": 0,
        "http_4xx": 0,
        "http_5xx": 1,
        "other": 0,
    }
    assert payload["result"]["peak_cpu_percent_generator"] == 22.0
    assert payload["result"]["peak_memory_rss_mb"] == 64.0
    assert payload["result"]["samples"][0]["system"]["cpu_percent_generator"] == 15.0
    assert payload["result"]["samples"][1]["requested_rate_per_minute"] == 250.0
