from pathlib import Path

from omega_stress.infrastructure.config import paths


def test_exports_dir_is_under_var(tmp_path):
    assert paths.exports_dir(tmp_path) == tmp_path / "exports"


def test_screenshots_dir_is_under_var():
    assert paths.screenshots_dir(Path("/base")) == Path("/base/screenshots")


def test_exports_and_screenshots_dirs_are_distinct_siblings(tmp_path):
    assert paths.exports_dir(tmp_path) != paths.screenshots_dir(tmp_path)
    assert paths.exports_dir(tmp_path).parent == paths.screenshots_dir(tmp_path).parent
