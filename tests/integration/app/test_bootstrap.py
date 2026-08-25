import sqlite3

import pytest

from omega_stress.app.bootstrap import bootstrap
from omega_stress.core.enums import ExportFormat


def test_bootstrap_wires_a_working_container(tmp_path):
    app = bootstrap(var_dir=tmp_path)

    assert app.container.profile_repository.list_all() == ()
    assert (tmp_path / "db" / "app.db").exists()
    assert (tmp_path / "app.log").exists()

    app.lifecycle.shutdown()


def test_bootstrap_wires_export_and_screenshot_dirs_under_var(tmp_path):
    app = bootstrap(var_dir=tmp_path)

    assert app.container.export_dir == tmp_path / "exports"
    assert app.container.screenshot_dir == tmp_path / "screenshots"

    app.lifecycle.shutdown()


def test_bootstrap_exposes_all_three_exporters(tmp_path):
    app = bootstrap(var_dir=tmp_path)

    assert set(app.container.exporters) == {
        ExportFormat.JSON,
        ExportFormat.CSV,
        ExportFormat.HTML,
    }

    app.lifecycle.shutdown()


def test_shutdown_closes_the_connection(tmp_path):
    app = bootstrap(var_dir=tmp_path)

    app.lifecycle.shutdown()

    with pytest.raises(sqlite3.ProgrammingError):
        app.container.connection.execute("SELECT 1")
