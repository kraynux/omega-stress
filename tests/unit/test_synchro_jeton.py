# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Jeton d'installation lu par omega-connect (contrats d'interconnexion, 2026-11-21)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from omega_lib.synchro.constants import TOOL_LAUNCHERS

from omega_stress.app import synchro_runner


def test_jeton_ecrit_au_format_omega(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "omega-stress"
    (root / "var").mkdir(parents=True)
    shutil.copy(Path(__file__).resolve().parents[2] / "pyproject.toml", root / "pyproject.toml")
    monkeypatch.setattr(synchro_runner, "project_root", lambda: root)
    assert synchro_runner.run_synchro(["jeton", "--format", "json"]) == 0
    printed = json.loads(capsys.readouterr().out)
    written = json.loads((root / "var" / "omega-jeton.json").read_text(encoding="utf-8"))
    assert printed == written
    assert written["format"] == "omega-jeton" and written["tool"] == "omega-stress"
    assert written["root"] == str(root.resolve())


def test_commande_inconnue_refusee(capsys: pytest.CaptureFixture[str]) -> None:
    assert synchro_runner.run_synchro(["fiche"]) == 2
    assert "usage" in capsys.readouterr().err


def test_omega_connect_connait_le_lanceur() -> None:
    assert TOOL_LAUNCHERS["omega-stress"] == "omega-stress.sh"
