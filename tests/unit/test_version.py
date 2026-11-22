# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""La version affichee (accueil, en-tete, aide) est lue dans pyproject.toml, seule source
(2026-11-22)."""

from __future__ import annotations

import re
from pathlib import Path

from omega_stress.core.constants import OMEGA_STRESS_VERSION
from omega_stress.interfaces.tui.widgets import splash_hero


def test_version_affichee_egale_pyproject() -> None:
    pyproject = (Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', pyproject, re.M)
    assert match is not None and match.group(1) == OMEGA_STRESS_VERSION
    assert f"v{OMEGA_STRESS_VERSION}" in splash_hero._VERSION_ROW
