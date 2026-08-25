import json
from datetime import datetime, timezone

from omega_stress.__main__ import main
from omega_stress.app.bootstrap import bootstrap
from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.runs.models import LoadResult, LoadRun
from omega_stress.domain.targets.models import Target, TargetAddress

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _seed_finished_run(tmp_path):
    """Persiste un run termine directement via le container, sans passer
    par `run request` (qui exigerait un reseau reel)."""
    app = bootstrap(var_dir=tmp_path)
    app.container.target_repository.save_recent(
        Target(id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW)
    )
    app.container.run_repository.save(
        LoadRun(
            id="run-1",
            profile_id=None,
            target_id="t-1",
            family=TestFamily.REQUEST,
            level=IntensityLevel.BAS,
            started_at=NOW,
            finished_at=NOW,
            result=LoadResult(
                verdict=RunVerdict.SUCCESS,
                requested_rate_per_minute=250,
                observed_rate_per_minute=248.0,
                p50_latency_ms=10.0,
                p95_latency_ms=20.0,
                p99_latency_ms=30.0,
                error_count=0,
                total_requests=250,
            ),
        )
    )
    app.lifecycle.shutdown()


def _run(monkeypatch, tmp_path, argv):
    monkeypatch.setenv("OMEGA_STRESS_VAR_DIR", str(tmp_path))
    return main(argv)


def test_history_list_and_show(monkeypatch, tmp_path, capsys):
    _seed_finished_run(tmp_path)

    exit_code = _run(monkeypatch, tmp_path, ["history", "list", "--json"])
    assert exit_code == 0
    runs = json.loads(capsys.readouterr().out)
    assert len(runs) == 1
    assert runs[0]["id"] == "run-1"

    exit_code = _run(monkeypatch, tmp_path, ["history", "show", "run-1", "--json"])
    assert exit_code == 0
    run = json.loads(capsys.readouterr().out)
    assert run["verdict"] == "success"


def test_history_show_unknown_run_fails_cleanly(monkeypatch, tmp_path, capsys):
    exit_code = _run(monkeypatch, tmp_path, ["history", "show", "does-not-exist"])

    assert exit_code == 1
    assert "introuvable" in capsys.readouterr().err


def test_export_json_writes_a_file(monkeypatch, tmp_path, capsys):
    _seed_finished_run(tmp_path)
    destination = tmp_path / "report.json"

    exit_code = _run(
        monkeypatch,
        tmp_path,
        ["export", "run-1", "--format", "json", "--destination", str(destination)],
    )

    assert exit_code == 0
    assert destination.exists()
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["summary"]["run_id"] == "run-1"


def test_export_unknown_run_fails_cleanly(monkeypatch, tmp_path, capsys):
    exit_code = _run(
        monkeypatch,
        tmp_path,
        ["export", "does-not-exist", "--format", "json", "--destination", str(tmp_path / "x.json")],
    )

    assert exit_code == 1
    assert "introuvable" in capsys.readouterr().err
