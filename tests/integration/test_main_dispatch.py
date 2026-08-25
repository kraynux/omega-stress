import json

import omega_stress.__main__ as main_module


class _StubApp:
    """Remplace OmegaStressApp pour verifier le dispatch sans demarrer un
    vrai terminal interactif (App.run() est bloquant et exigerait un
    driver reel)."""

    instances: list["_StubApp"] = []

    def __init__(self, container) -> None:
        self.container = container
        self.ran = False
        _StubApp.instances.append(self)

    def run(self) -> None:
        self.ran = True


def test_no_arguments_launches_the_tui(monkeypatch, tmp_path):
    monkeypatch.setenv("OMEGA_STRESS_VAR_DIR", str(tmp_path))
    _StubApp.instances.clear()
    monkeypatch.setattr(main_module, "OmegaStressApp", _StubApp)

    exit_code = main_module.main([])

    assert exit_code == 0
    assert len(_StubApp.instances) == 1
    assert _StubApp.instances[0].ran is True


def test_a_recognized_subcommand_launches_the_cli_instead(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("OMEGA_STRESS_VAR_DIR", str(tmp_path))
    _StubApp.instances.clear()
    monkeypatch.setattr(main_module, "OmegaStressApp", _StubApp)

    exit_code = main_module.main(["profile", "list", "--json"])

    assert exit_code == 0
    assert _StubApp.instances == []
    assert json.loads(capsys.readouterr().out) == []


def test_none_argv_falls_back_to_real_sys_argv(monkeypatch, tmp_path):
    monkeypatch.setenv("OMEGA_STRESS_VAR_DIR", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["omega-stress"])
    _StubApp.instances.clear()
    monkeypatch.setattr(main_module, "OmegaStressApp", _StubApp)

    exit_code = main_module.main(None)

    assert exit_code == 0
    assert len(_StubApp.instances) == 1
