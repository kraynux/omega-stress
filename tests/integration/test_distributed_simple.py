# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Charge distribuee, parcours simple (2026-11-21) : ce qu'omega-connect fait a la place de
l'utilisateur (acces cree chez le pilote, machine qui aide reliee par SSH, secret par l'entree
standard), test lance par SSH a chaque fois, accord « Demander » / « Tout accepter », pare-feu.

Un faux `ssh` (en tete du PATH) execute la commande recue sur cette machine, dans le dossier var/ de
la « machine » visee, comme le ferait sshd."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from omega_stress.app.distributed_runner import run_coordinator, run_worker
from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.infrastructure.distributed import firewall
from omega_stress.infrastructure.distributed.coordinator import DistributedLoadGenerator
from omega_stress.infrastructure.distributed.store import DistributedStore
from omega_stress.infrastructure.runner.engine_params import IntervalTarget

PROJECT = Path(__file__).resolve().parents[2]


@pytest.fixture
def target_url() -> Iterator[str]:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()


@pytest.fixture
def fleet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Faux ssh : « utilisateur@hote » -> var/ = <tmp>/machines/<utilisateur@hote>."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "ssh").write_text(
        "#!/usr/bin/env bash\n"
        'while [ "${1:-}" = "-o" ]; do shift 2; done\n'
        'echo "$1 $2" >> "$OMEGA_FAKE_ROOT/ssh.log"\n'
        'export OMEGA_STRESS_VAR_DIR="$OMEGA_FAKE_ROOT/machines/$1"\n'
        "shift\n"
        # Comme craftdark (Archcraft, 2026-11-21) : sans terminal, le PATH ne contient presque
        # rien ; chaque commande distante doit retablir le PATH standard elle-meme.
        'PATH=/usr/share/archcraft/scripts exec /bin/bash -c "$*"\n'
    )
    (fake_bin / "ssh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    monkeypatch.setenv("OMEGA_FAKE_ROOT", str(tmp_path))
    return tmp_path


def _connect_links(fleet: Path, capsys: pytest.CaptureFixture[str], name: str, accord: str) -> str:
    """Ce que fera omega-connect pour relier une machine qui aide : acces cree chez le pilote, puis
    `worker relier` sur la machine qui aide, secret par l'entree standard (jamais en argument)."""
    ssh = f"{name}@127.0.0.1"
    capsys.readouterr()
    assert (
        run_coordinator(
            [
                "ajouter-machine",
                "--nom",
                name,
                "--ssh",
                ssh,
                "--chemin",
                str(PROJECT),
                "--format",
                "json",
            ],
            var_dir=fleet / "pilote",
        )
        == 0
    )
    access = json.loads(capsys.readouterr().out)
    result = subprocess.run(
        [
            "ssh",
            ssh,
            "export PATH=/usr/local/bin:/usr/bin:/bin:$PATH; "
            f"cd {PROJECT} && ./omega-stress.sh worker relier --pilote-adresse 127.0.0.1:"
            f"{access['port']} --pilote-empreinte {access['fingerprint']} --id {access['id']} "
            f"--accord {accord}",
        ],
        input=access["secret"] + "\n",
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert access["secret"] not in (fleet / "ssh.log").read_text()  # jamais en argument
    return str(access["id"])


def _free_port() -> int:
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _run(
    fleet: Path, url: str, machines: tuple[str, ...], rps: float, seconds: int, **options: object
) -> tuple[list, list[str]]:
    notes: list[str] = []
    generator = DistributedLoadGenerator(
        DistributedStore(fleet / "pilote"),
        port=_free_port(),
        machines=machines,
        notify=notes.append,
        join_timeout_seconds=60,
        **options,  # type: ignore[arg-type]
    )

    async def go() -> list:
        return [
            s
            async for s in generator.stream(
                [IntervalTarget(rps, 0)] * seconds, target_url=url, duration_minutes=1
            )
        ]

    return asyncio.run(go()), notes


def test_relie_par_omega_connect_puis_lance_par_ssh(
    fleet: Path, target_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    machine = _connect_links(fleet, capsys, "b", "tout")
    samples, notes = _run(fleet, target_url, (machine,), 30.0, 2)
    assert [s.emitted_count for s in samples] == [30, 30]
    assert all(s.error_count == 0 for s in samples)
    # le pilote a trouve seul son adresse et s'est fait reconnaitre par son empreinte
    log = (fleet / "ssh.log").read_text()
    assert "worker rejoindre 127.0.0.1:" in log and "--pilote " in log


def test_cette_machine_charge_aussi_si_cochee(
    fleet: Path, target_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    machine = _connect_links(fleet, capsys, "b", "tout")
    samples, _notes = _run(fleet, target_url, (machine,), 40.0, 2, include_local=True)
    assert [s.emitted_count for s in samples] == [40, 40]  # reparti entre B et cette machine
    only_local, _ = _run(fleet, target_url, (), 20.0, 2, include_local=True)
    assert [s.emitted_count for s in only_local] == [20, 20]


def test_accord_demander(fleet: Path, target_url: str, capsys: pytest.CaptureFixture[str]) -> None:
    machine = _connect_links(fleet, capsys, "b", "demander")
    asked: list[tuple[str, str]] = []

    async def refuse(name: str, target: str) -> bool:
        asked.append((name, target))
        return False

    with pytest.raises(RunnerFailureError, match="Aucune machine"):
        _run(fleet, target_url, (machine,), 10.0, 1, approve=refuse)
    assert asked and asked[0][1] == target_url.rstrip("/")

    async def accept(name: str, target: str) -> bool:
        return True

    samples, _notes = _run(fleet, target_url, (machine,), 10.0, 1, approve=accept)
    assert samples[0].emitted_count == 10
    # accord ecrit SUR la machine qui aide : plus de question la fois suivante
    worker = DistributedStore(fleet / "machines" / "b@127.0.0.1").authorization()
    assert worker is not None and target_url.rstrip("/") in worker.targets
    samples, _ = _run(fleet, target_url, (machine,), 10.0, 1, approve=refuse)
    assert samples[0].emitted_count == 10


def test_limites_pre_remplies_et_etat_json(fleet: Path, capsys: pytest.CaptureFixture[str]) -> None:
    machine = _connect_links(fleet, capsys, "b", "demander")
    var_b = fleet / "machines" / "b@127.0.0.1"
    capsys.readouterr()
    assert run_worker(["etat", "--format", "json"], var_dir=var_b) == 0
    state = json.loads(capsys.readouterr().out)
    auth = state["authorization"]
    assert auth["max_requests_per_minute"] > 0 and auth["max_duration_minutes"] == 60
    assert auth["accept_all_targets"] is False and len(auth["coordinators"]) == 1
    assert run_coordinator(["etat", "--format", "json"], var_dir=fleet / "pilote") == 0
    pilot = json.loads(capsys.readouterr().out)
    assert [m["id"] for m in pilot["machines"]] == [machine]
    assert "secret" not in json.dumps(pilot)
    assert run_coordinator(["retirer-machine", machine], var_dir=fleet / "pilote") == 0
    assert DistributedStore(fleet / "pilote").workers() == {}


def test_pare_feu_commandes() -> None:
    nets = ("192.168.1.0/24",)
    assert firewall.open_commands(firewall.UFW, nets, 9650) == [
        [
            "ufw",
            "allow",
            "from",
            "192.168.1.0/24",
            "to",
            "any",
            "port",
            "9650",
            "proto",
            "tcp",
            "comment",
            "omega-stress",
        ]
    ]
    assert firewall.close_commands(firewall.UFW, nets, 9650)[0][:3] == ["ufw", "delete", "allow"]
    assert firewall.open_commands(firewall.FIREWALLD, nets, 9650)[-1] == [
        "firewall-cmd",
        "--reload",
    ]
    assert firewall.open_commands(firewall.OTHER, nets, 9650) == []
    state = firewall.FirewallState(firewall.UFW, nets, 9650, opened=False)
    assert state.needs_opening
    assert not firewall.FirewallState(firewall.NONE, nets, 9650, opened=False).needs_opening


def test_pare_feu_commandes_puis_fait(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """omega-connect demande les commandes, les lance dans sa propre invite sudo, puis le note."""
    monkeypatch.setattr(firewall, "detect_backend", lambda: firewall.UFW)
    monkeypatch.setattr(firewall, "private_networks", lambda: ("192.168.1.0/24",))
    capsys.readouterr()
    assert run_coordinator(["pare-feu", "ouvrir", "--commandes"], var_dir=tmp_path) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["backend"] == "ufw" and len(plan["commands"]) == 1
    assert run_coordinator(["pare-feu", "ouvrir", "--fait"], var_dir=tmp_path) == 0
    assert run_coordinator(["pare-feu", "etat", "--format", "json"], var_dir=tmp_path) == 0
    assert json.loads(capsys.readouterr().out)["opened"] is True
    assert run_coordinator(["pare-feu", "fermer", "--commandes"], var_dir=tmp_path) == 0
    assert json.loads(capsys.readouterr().out)["commands"][0][:2] == ["ufw", "delete"]


def test_pare_feu_omega_fire_d_abord(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """omega-fire relie par omega-connect : c'est lui qui ouvre (et referme) le port, quel que soit
    le pare-feu ; nftables seul sans omega-fire : rien n'est touche, omega-fire est demande."""
    fire = tmp_path / "omega-fire.sh"
    monkeypatch.setattr(firewall, "omega_fire_launcher", lambda: str(fire))
    monkeypatch.setattr(firewall, "_active", lambda unit: unit == "nftables")
    monkeypatch.setattr(firewall, "private_networks", lambda: ("192.168.1.0/24", "100.64.0.0/10"))
    capsys.readouterr()
    assert run_coordinator(["pare-feu", "ouvrir", "--commandes"], var_dir=tmp_path) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan == {
        "backend": "omega-fire",
        "commands": [
            [
                str(fire),
                "port",
                "ouvrir",
                "--port",
                "9650",
                "--sources",
                "192.168.1.0/24,100.64.0.0/10",
                "--pour",
                "omega-stress",
                "--format",
                "json",
            ]
        ],
    }
    assert run_coordinator(["pare-feu", "ouvrir", "--fait"], var_dir=tmp_path) == 0
    assert run_coordinator(["pare-feu", "fermer", "--commandes"], var_dir=tmp_path) == 0
    assert json.loads(capsys.readouterr().out)["commands"][0][1:3] == ["port", "fermer"]

    monkeypatch.setattr(firewall, "omega_fire_launcher", lambda: "")
    other = tmp_path / "autre"
    assert run_coordinator(["pare-feu", "etat", "--format", "json"], var_dir=other) == 0
    state = json.loads(capsys.readouterr().out)
    assert state["backend"] == "nftables" and state["needs_omega_fire"] is True
    assert run_coordinator(["pare-feu", "ouvrir"], var_dir=other) == 1
    assert "omega-fire est nécessaire" in capsys.readouterr().out


def test_pare_feu_jamais_de_sudo_sans_terminal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Piege pam_faillock : sans terminal, aucune commande sudo n'est lancee."""
    monkeypatch.setattr(firewall, "detect_backend", lambda: firewall.UFW)
    monkeypatch.setattr(firewall, "private_networks", lambda: ("192.168.1.0/24",))
    launched: list[list[str]] = []
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kw: launched.append(command),  # type: ignore[misc]
    )
    monkeypatch.setattr("sys.stdin", open(os.devnull))  # noqa: SIM115
    assert run_coordinator(["pare-feu", "ouvrir"], var_dir=tmp_path) == 1
    assert launched == []
    assert "terminal est nécessaire" in capsys.readouterr().out


def test_bilan_par_machine(
    fleet: Path, target_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Retour de l'auteur (2026-11-21) : « aucun moyen de savoir si craftdark a participe »."""
    machine = _connect_links(fleet, capsys, "b", "tout")
    notes: list[str] = []
    generator = DistributedLoadGenerator(
        DistributedStore(fleet / "pilote"),
        port=_free_port(),
        machines=(machine,),
        include_local=True,
        notify=notes.append,
        join_timeout_seconds=60,
    )

    async def go() -> list:
        return [
            s
            async for s in generator.stream(
                [IntervalTarget(20.0, 0)] * 2, target_url=target_url, duration_minutes=1
            )
        ]

    samples = asyncio.run(go())
    summary = generator.participation_summary()
    assert "b : " in summary and "cette machine : " in summary
    emitted = sum(s.emitted_count for s in samples)
    numbers = [
        int(part.split(" requêtes émises")[0].rsplit(" ", 1)[-1]) for part in summary.split(" ; ")
    ]
    assert sum(numbers) == emitted == 40 and all(n > 0 for n in numbers)
    assert any("a rejoint le pilote" in n for n in notes)
    assert any(n.startswith("Départ") for n in notes)
    assert notes[-1] == summary


def test_compte_rendu_pare_feu_enregistre(tmp_path: Path) -> None:
    """Qui a ouvert, quand, quel gestionnaire, quelles regles (numeros omega-fire)."""
    from omega_stress.infrastructure.distributed.services import DistributedServices

    services = DistributedServices(tmp_path)
    answer = json.dumps(
        {
            "ok": True,
            "lignes": [
                {
                    "cible": "nftables",
                    "source": "192.168.1.0/24",
                    "etat": "ajoutee",
                    "detail": "#12",
                }
            ],
        }
    )
    services.note_firewall(
        True,
        firewall.OMEGA_FIRE,
        ("192.168.1.0/24",),
        by="omega-connect",
        commands=[["omega-fire.sh", "port", "ouvrir"]],
        outputs=["avant\n" + answer],
    )
    record = services.firewall_record()
    assert record["opened_by"] == "omega-connect" and record["opened_at"]
    assert record["rules"] == [
        {"manager": "nftables", "network": "192.168.1.0/24", "state": "ajoutee", "rule": "#12"}
    ]
    ufw = firewall.rule_report(
        firewall.UFW, firewall.open_commands(firewall.UFW, ("10.0.0.0/8",), 9650), []
    )
    assert ufw[0]["manager"] == "ufw" and ufw[0]["network"] == "10.0.0.0/8"
    services.note_firewall(False, firewall.OMEGA_FIRE, ("192.168.1.0/24",))
    assert services.firewall_record()["closed_by"] == "omega-stress"
    assert services.participating() == ((), False)
