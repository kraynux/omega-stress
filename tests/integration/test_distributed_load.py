# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Charge distribuee (Phase 2, 2026-11-21) : coordinateur et workers reels (TLS, processus
d'emission), sur cette machine, contre un vrai serveur HTTP local."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.domain.distributed.policies import (
    WorkerAuthorization,
    allocate,
    origin_of,
    refusal_reason,
    split_whole,
)
from omega_stress.domain.load.histogram import count
from omega_stress.infrastructure.distributed import worker_agent
from omega_stress.infrastructure.distributed.coordinator import (
    Coordinator,
    DistributedLoadGenerator,
)
from omega_stress.infrastructure.distributed.protocol import ProtocolError
from omega_stress.infrastructure.distributed.store import DistributedStore
from omega_stress.infrastructure.runner.engine_params import IntervalTarget


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


def _authorize(store: DistributedStore, target: str, rpm: int = 60_000) -> None:
    store.save_authorization(
        WorkerAuthorization((), (target,), rpm, max_duration_minutes=10, max_connections=100)
    )


async def _pair_workers(
    coordinator_dir: Path, worker_dirs: list[Path], target: str, port: int
) -> DistributedStore:
    """Appairage reel : le coordinateur ecoute, chaque worker presente un code a usage unique."""
    coordinator_store = DistributedStore(coordinator_dir)
    coordinator = Coordinator(coordinator_store, port, host="127.0.0.1")
    await coordinator.start()
    try:
        for directory in worker_dirs:
            store = DistributedStore(directory)
            _authorize(store, target)
            code = coordinator_store.new_pairing_code()
            await worker_agent.pair(
                store, f"127.0.0.1:{coordinator.port}", coordinator.fingerprint, code
            )
    finally:
        await coordinator.stop()
    return coordinator_store


def _free_port() -> int:
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _campaign(
    tmp_path: Path,
    target: str,
    targets: list[IntervalTarget],
    *,
    workers: int = 2,
    capacities: list[float] | None = None,
    tweak: object = None,
    kill_first_after: float | None = None,
) -> tuple[list, list[str]]:
    port = _free_port()
    worker_dirs = [tmp_path / f"w{i}" for i in range(workers)]
    store = await _pair_workers(tmp_path / "coord", worker_dirs, target, port)
    if callable(tweak):
        tweak(worker_dirs)
    notes: list[str] = []
    generator = DistributedLoadGenerator(
        store, port=port, expected_workers=workers, notify=notes.append, join_timeout_seconds=20
    )
    generator_stream = generator.stream(targets, target_url=target, duration_minutes=1)
    joins = [
        asyncio.ensure_future(
            worker_agent.join(
                DistributedStore(directory),
                f"127.0.0.1:{port}",
                version="test",
                once=True,
                log=lambda _m: None,
                capacity_rps=(capacities or [1000.0] * workers)[index],
                wait_seconds=20,
            )
        )
        for index, directory in enumerate(worker_dirs)
    ]

    async def start_workers_later() -> None:
        if kill_first_after is not None:  # panne d'un worker en cours de campagne
            await asyncio.sleep(kill_first_after)
            joins[0].cancel()

    samples = []
    started = asyncio.ensure_future(start_workers_later())
    try:
        async for sample in generator_stream:
            samples.append(sample)
    finally:
        await started
        await asyncio.wait_for(asyncio.gather(*joins, return_exceptions=True), 30)
    return samples, notes


def test_deux_workers_emettent_le_debit_demande(tmp_path: Path, target_url: str) -> None:
    samples, notes = asyncio.run(
        _campaign(tmp_path, target_url, [IntervalTarget(60.0, 0)] * 3, capacities=[2000.0, 1000.0])
    )
    assert [s.emitted_count for s in samples] == [60, 60, 60]
    assert all(s.error_count == 0 for s in samples)
    assert sum(s.request_count for s in samples) >= 170
    assert all(count(s.latency_histogram) == s.request_count for s in samples)
    assert not any("écarté" in note or "perdu" in note for note in notes)


def test_worker_qui_refuse_est_ecarte(tmp_path: Path, target_url: str) -> None:
    def forbid_first(dirs: list[Path]) -> None:
        _authorize(DistributedStore(dirs[0]), "http://autre-cible.example")
        # coordinateur toujours accepte (empreinte gardee par l'appairage)
        store = DistributedStore(dirs[0])
        previous = DistributedStore(dirs[1]).authorization()
        assert previous is not None
        auth = store.authorization()
        assert auth is not None
        from dataclasses import replace

        store.save_authorization(replace(auth, coordinators=previous.coordinators))

    samples, notes = asyncio.run(
        _campaign(tmp_path, target_url, [IntervalTarget(40.0, 0)] * 2, tweak=forbid_first)
    )
    assert any("écartée" in note and "non autorisée" in note for note in notes)
    assert [s.emitted_count for s in samples] == [40, 40]  # part reprise par l'autre worker


def test_au_dela_de_la_capacite_campagne_refusee(tmp_path: Path, target_url: str) -> None:
    with pytest.raises(RunnerFailureError, match="capacité des machines"):
        asyncio.run(
            _campaign(tmp_path, target_url, [IntervalTarget(500.0, 0)], capacities=[100.0, 100.0])
        )


def test_appairage_code_et_empreinte(tmp_path: Path) -> None:
    async def go() -> None:
        store = DistributedStore(tmp_path / "coord")
        coordinator = Coordinator(store, 0, host="127.0.0.1")
        await coordinator.start()
        address = f"127.0.0.1:{coordinator.port}"
        worker = DistributedStore(tmp_path / "w")
        try:
            with pytest.raises(ProtocolError, match="fingerprint"):
                await worker_agent.pair(worker, address, "00" * 32, store.new_pairing_code())
            with pytest.raises(ProtocolError, match="pairing code"):
                await worker_agent.pair(worker, address, coordinator.fingerprint, "FAUX0000")
            code = store.new_pairing_code()
            await worker_agent.pair(worker, address, coordinator.fingerprint, code)
            with pytest.raises(ProtocolError, match="pairing code"):  # usage unique
                await worker_agent.pair(worker, address, coordinator.fingerprint, code)
        finally:
            await coordinator.stop()
        record = worker.coordinators()[coordinator.fingerprint]
        assert store.check_worker(record["worker_id"], record["secret"]) is not None
        assert store.check_worker(record["worker_id"], "mauvais") is None
        # seule l'empreinte du secret est gardee par le coordinateur
        assert record["secret"] not in str(store.workers())
        assert (tmp_path / "coord" / "distributed" / "coordinateur.key").stat().st_mode & 0o077 == 0

    asyncio.run(go())


def test_regles_autorisation_et_repartition() -> None:
    auth = WorkerAuthorization(("abc",), ("https://cible.lan",), 6000, 30, 200)
    ok = dict(
        coordinator="abc",
        target_url="https://CIBLE.lan:443/page?x=1",
        duration_minutes=30,
        peak_requests_per_minute=6000,
        peak_connections=200,
    )
    assert refusal_reason(auth, **ok) is None
    assert refusal_reason(None, **ok) is not None
    assert "coordinator" in (refusal_reason(auth, **{**ok, "coordinator": "x"}) or "")
    assert "approval needed" in (
        refusal_reason(auth, **{**ok, "target_url": "https://a.lan"}) or ""
    )
    assert "approval" in (refusal_reason(auth, **{**ok, "target_url": "http://cible.lan"}) or "")
    from dataclasses import replace

    assert (
        refusal_reason(
            replace(auth, accept_all_targets=True), **{**ok, "target_url": "https://a.lan"}
        )
        is None
    )
    assert "duration" in (refusal_reason(auth, **{**ok, "duration_minutes": 31}) or "")
    assert "rate" in (refusal_reason(auth, **{**ok, "peak_requests_per_minute": 6001}) or "")
    assert "connections" in (refusal_reason(auth, **{**ok, "peak_connections": 201}) or "")
    assert origin_of("http://h:80/x") == "http://h"
    assert allocate(300.0, [200.0, 100.0]) == [200.0, 100.0]
    assert allocate(150.0, [200.0, 100.0]) == [100.0, 50.0]
    assert allocate(301.0, [200.0, 100.0]) is None
    assert split_whole(7, [2.0, 1.0]) == [5, 2]
    assert sum(split_whole(1000, [0.3, 0.3, 0.4])) == 1000


def test_worker_perdu_signale_et_run_continue(tmp_path: Path, target_url: str) -> None:
    samples, notes = asyncio.run(
        _campaign(tmp_path, target_url, [IntervalTarget(40.0, 0)] * 6, kill_first_after=4.0)
    )
    assert len(samples) == 6
    assert any("perdue à la seconde" in note for note in notes)
    assert samples[0].emitted_count == 40
    assert 0 < samples[-1].emitted_count < 40  # mesure incomplete, signalee


def test_mode_pousse_par_ssh(
    tmp_path: Path, target_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Le coordinateur lance `omega-stress.sh worker rejoindre … --une-fois` par SSH : un faux
    `ssh` (en tete du PATH) execute la commande recue sur cette machine, comme le ferait sshd."""
    project = Path(__file__).resolve().parents[2]
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "ssh").write_text(
        "#!/usr/bin/env bash\n"
        'while [ "${1:-}" = "-o" ]; do shift 2; done\n'
        'echo "$1" >> "$OMEGA_FAKE_SSH_LOG"\n'
        "shift\n"
        'exec bash -c "$*"\n'
    )
    (fake_bin / "ssh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake_bin}:{__import__('os').environ['PATH']}")
    monkeypatch.setenv("OMEGA_FAKE_SSH_LOG", str(tmp_path / "ssh.log"))
    monkeypatch.setenv("OMEGA_STRESS_VAR_DIR", str(tmp_path / "w0"))
    port = _free_port()

    async def go() -> tuple[list, list[str]]:
        store = await _pair_workers(tmp_path / "coord", [tmp_path / "w0"], target_url, port)
        notes: list[str] = []
        generator = DistributedLoadGenerator(
            store,
            port=port,
            expected_workers=0,  # la machine lancee par --ssh compte d'elle-même
            ssh_targets=(f"moi@machine-a:{project}",),
            announce="127.0.0.1",
            notify=notes.append,
            join_timeout_seconds=60,
        )
        samples = [
            s
            async for s in generator.stream(
                [IntervalTarget(20.0, 0)] * 2, target_url=target_url, duration_minutes=1
            )
        ]
        return samples, notes

    samples, notes = asyncio.run(go())
    assert (tmp_path / "ssh.log").read_text().split() == ["moi@machine-a"]
    assert notes
    assert [s.emitted_count for s in samples] == [20, 20]
