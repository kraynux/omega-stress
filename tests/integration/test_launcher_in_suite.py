# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Copie embarquee par omega-suite (decision de l'auteur, 2026-11-22) :
`<suite>/vendor/omega-stress/omega-stress.sh` prend le .venv de la suite et son var/stress
(celui de l'onglet omega-stress) ; autonome, rien ne change. Le « python » est un faux qui
affiche ce qu'il recoit : aucun omega-stress n'est lance."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "omega-stress.sh"
FAKE_PYTHON = "#!/bin/sh\necho \"python=$0 var=${OMEGA_STRESS_VAR_DIR:-} cwd=$(pwd)\"\n"


def _python(folder: Path) -> None:
    (folder / ".venv" / "bin").mkdir(parents=True)
    python = folder / ".venv" / "bin" / "python"
    python.write_text(FAKE_PYTHON)
    python.chmod(0o755)


def _run(launcher: Path, *args: str, env: dict[str, str] | None = None) -> str:
    environment = {"PATH": "/usr/bin:/bin", **(env or {})}
    done = subprocess.run([str(launcher), *args], capture_output=True, text=True, check=False,
                          cwd="/", env=environment, timeout=30)
    return done.stdout.strip().splitlines()[-1]


def _suite(tmp: Path) -> tuple[Path, Path]:
    suite = tmp / "omega-suite"
    embedded = suite / "vendor" / "omega-stress"
    embedded.mkdir(parents=True)
    shutil.copy2(LAUNCHER, embedded / "omega-stress.sh")
    (suite / "omega-suite.sh").write_text("#!/bin/sh\n")
    _python(suite)
    return suite, embedded


def test_copie_embarquee_prend_le_venv_et_le_var_de_la_suite(tmp_path: Path) -> None:
    suite, embedded = _suite(tmp_path)
    for args in (("worker", "etat"), ("--help",)):
        line = _run(embedded / "omega-stress.sh", *args)
        expected = f"python={suite}/.venv/bin/python var={suite}/var/stress cwd={embedded}"
        assert line == expected, args
    moved = _run(embedded / "omega-stress.sh", "synchro",
                 env={"OMEGA_SUITE_VAR_DIR": str(tmp_path / "ailleurs")})
    assert f"var={tmp_path}/ailleurs/stress" in moved


def test_autonome_ou_copie_avec_son_venv_inchange(tmp_path: Path) -> None:
    alone = tmp_path / "omega-stress"
    alone.mkdir()
    shutil.copy2(LAUNCHER, alone / "omega-stress.sh")
    _python(alone)
    expected = f"python={alone}/.venv/bin/python var= cwd={alone}"
    assert _run(alone / "omega-stress.sh", "worker") == expected
    _suite_dir, embedded = _suite(tmp_path / "s")
    _python(embedded)  # la copie a son propre .venv : c'est lui qui compte
    line = _run(embedded / "omega-stress.sh", "worker")
    assert line.startswith(f"python={embedded}/.venv/bin/python var= ")
