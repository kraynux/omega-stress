from omega_stress.core.enums import ExportFormat
from omega_stress.infrastructure.exporters.html_exporter import HtmlReportExporter

from .conftest import make_job


def test_export_writes_html_with_expected_content(tmp_path, report_content):
    job = make_job(
        tmp_path, fmt=ExportFormat.HTML, filename="report.html", export_theme="omega-neon"
    )
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "run-1" in html
    assert "success" in html
    assert "#ff00ff" in html  # accent d'omega-neon


def test_unknown_theme_falls_back_to_default(tmp_path, report_content):
    job = make_job(
        tmp_path, fmt=ExportFormat.HTML, filename="report.html", export_theme="does-not-exist"
    )
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "#00d4ff" in html  # accent d'omega-base, le theme par defaut


def test_timeline_section_appears_with_samples(tmp_path, report_content_with_samples):
    job = make_job(tmp_path, fmt=ExportFormat.HTML, filename="report.html")
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content_with_samples, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "Chronologie" in html
    assert "2 mesures" in html


def test_timeline_section_is_omitted_without_samples(tmp_path, report_content):
    job = make_job(tmp_path, fmt=ExportFormat.HTML, filename="report.html")
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "Chronologie" not in html


def test_charts_appear_with_samples(tmp_path, report_content_with_samples):
    job = make_job(tmp_path, fmt=ExportFormat.HTML, filename="report.html")
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content_with_samples, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "Graphiques" in html
    # RPS, latence, CPU au minimum (donnees presentes sur les fixtures).
    assert html.count("<svg") >= 3


def test_charts_section_is_omitted_without_samples(tmp_path, report_content):
    job = make_job(tmp_path, fmt=ExportFormat.HTML, filename="report.html")
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "Graphiques" not in html


def test_peak_system_metrics_appear_in_metrics_box(tmp_path, report_content_with_samples):
    job = make_job(tmp_path, fmt=ExportFormat.HTML, filename="report.html")
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content_with_samples, job)

    with open(written_path, encoding="utf-8") as handle:
        html = handle.read()
    assert "Pic CPU generateur" in html
    assert "22" in html


def test_export_to_an_existing_folder_derives_a_filename_instead_of_crashing(
    tmp_path, report_content
):
    """Reproduit un incident reel (2026-08-24) : choisir un dossier deja
    existant (ex. var/exports) comme destination levait IsADirectoryError
    -> StorageError -> plantage complet de l'application (aucun filet de
    securite TUI a l'epoque, voir interfaces/tui/app.py::
    _handle_exception())."""
    job = make_job(tmp_path, fmt=ExportFormat.HTML, filename="")
    exporter = HtmlReportExporter()

    written_path = exporter.export(report_content, job)

    assert written_path == str(tmp_path / "test-requetes-20260824-100000.html")
