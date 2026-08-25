import json

from omega_stress.__main__ import main


def _run(monkeypatch, tmp_path, argv):
    monkeypatch.setenv("OMEGA_STRESS_VAR_DIR", str(tmp_path))
    return main(argv)


def test_create_then_list_then_freeze(monkeypatch, tmp_path, capsys):
    exit_code = _run(
        monkeypatch,
        tmp_path,
        [
            "profile",
            "create",
            "--name",
            "Charge nominale",
            "--target-id",
            "t-1",
            "--family",
            "request",
            "--level",
            "bas",
            "--duration-minutes",
            "1",
            "--max-error-rate",
            "0.1",
            "--json",
        ],
    )
    assert exit_code == 0
    created = json.loads(capsys.readouterr().out)
    assert created["name"] == "Charge nominale"
    assert created["frozen"] is False

    exit_code = _run(monkeypatch, tmp_path, ["profile", "list", "--json"])
    assert exit_code == 0
    listed = json.loads(capsys.readouterr().out)
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]

    exit_code = _run(monkeypatch, tmp_path, ["profile", "freeze", created["id"], "--json"])
    assert exit_code == 0
    frozen = json.loads(capsys.readouterr().out)
    assert frozen["frozen"] is True


def test_create_with_invalid_duration_fails_cleanly(monkeypatch, tmp_path, capsys):
    exit_code = _run(
        monkeypatch,
        tmp_path,
        [
            "profile",
            "create",
            "--name",
            "Trop long",
            "--target-id",
            "t-1",
            "--family",
            "request",
            "--level",
            "haut",
            "--duration-minutes",
            "5",
            "--max-error-rate",
            "0.1",
        ],
    )
    assert exit_code == 1
    assert "Erreur" in capsys.readouterr().err


def test_freeze_unknown_profile_fails_cleanly(monkeypatch, tmp_path, capsys):
    exit_code = _run(monkeypatch, tmp_path, ["profile", "freeze", "does-not-exist"])

    assert exit_code == 1
    assert "introuvable" in capsys.readouterr().err


def test_human_readable_output_by_default(monkeypatch, tmp_path, capsys):
    exit_code = _run(
        monkeypatch,
        tmp_path,
        [
            "profile",
            "create",
            "--name",
            "Charge nominale",
            "--target-id",
            "t-1",
            "--family",
            "request",
            "--level",
            "bas",
            "--duration-minutes",
            "1",
            "--max-error-rate",
            "0.1",
        ],
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Profil" in out
    assert "Charge nominale" in out
