# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Moteur en boucle ouverte multiprocessus (Phase 0 + 1, 2026-11-21), contre de vrais serveurs HTTP
locaux."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

import pytest

from omega_stress.domain.load.histogram import count, histogram_of, merge, percentile_ms
from omega_stress.infrastructure.runner.engine_params import IntervalTarget
from omega_stress.infrastructure.runner.open_loop.generator import (
    OpenLoopLoadGenerator,
    process_count,
    split_count,
)


def _server(delay: float, threaded: bool, serial: bool = False) -> tuple[HTTPServer, str]:
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:  # noqa: N802
            if serial:
                with lock:  # toutes les connexions acceptees, mais une requete traitee a la fois
                    time.sleep(delay)
            elif delay:
                time.sleep(delay)
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args: object) -> None:
            pass

    server_class = ThreadingHTTPServer if threaded else HTTPServer
    server = server_class(("127.0.0.1", 0), Handler)
    server.daemon_threads = True  # type: ignore[attr-defined]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


@pytest.fixture
def fast_server() -> Iterator[str]:
    server, url = _server(0.0, threaded=True)
    yield url
    server.shutdown()


def _collect(generator: OpenLoopLoadGenerator, targets: list[IntervalTarget], url: str) -> list:
    async def go() -> list:
        return [sample async for sample in generator.stream(targets, target_url=url)]

    return asyncio.run(go())


def test_emis_egal_au_debit_demande(fast_server: str) -> None:
    samples = _collect(
        OpenLoopLoadGenerator(processes=1), [IntervalTarget(40.0, 0)] * 3, fast_server
    )
    assert [s.emitted_count for s in samples] == [40, 40, 40]
    assert all(s.not_emitted_count == 0 and s.error_count == 0 for s in samples)
    assert sum(s.request_count for s in samples) >= 110
    assert all(count(s.latency_histogram) == s.request_count for s in samples)
    assert samples[-1].requested_rate_per_minute == 2400.0


def test_cible_saturee_fait_monter_la_latence() -> None:
    """Omission coordonnee corrigee : un serveur qui traite une requete a la fois (50 ms, 20 req/s)
    en recoit 40 ; l'emission continue au meme rythme et la latence (depuis l'instant prevu)
    grimpe au lieu d'etre masquee."""
    server, url = _server(0.05, threaded=True, serial=True)
    try:
        samples = _collect(OpenLoopLoadGenerator(processes=1), [IntervalTarget(40.0, 0)] * 4, url)
    finally:
        server.shutdown()
    assert all(s.emitted_count == 40 for s in samples)
    assert samples[-1].p50_latency_ms > 3 * samples[0].p50_latency_ms
    assert samples[-1].active_connections > 20  # requetes en attente de la cible


def test_plafond_en_vol_compte_les_non_emises() -> None:
    server, url = _server(0.5, threaded=True)
    try:
        samples = _collect(
            OpenLoopLoadGenerator(processes=1, inflight_cap=5), [IntervalTarget(30.0, 0)] * 2, url
        )
    finally:
        server.shutdown()
    assert sum(s.not_emitted_count for s in samples) > 20
    assert all(s.emitted_count + s.not_emitted_count == 30 for s in samples)


def test_connexions_tenues_lecture_b(fast_server: str) -> None:
    samples = _collect(
        OpenLoopLoadGenerator(processes=2), [IntervalTarget(0.0, 30)] * 3, fast_server
    )
    assert samples[-1].active_connections == 30
    assert 1 <= samples[-1].emitted_count <= 6  # ~30 / 10 s par seconde
    assert all(s.error_count == 0 for s in samples)


def test_dimensionnement_et_repartition() -> None:
    assert process_count([IntervalTarget(10.0, 0)], cpu_count=8) == 1
    assert process_count([IntervalTarget(3000.0, 0)], cpu_count=8) == 3
    assert process_count([IntervalTarget(3000.0, 0)], cpu_count=2) == 1
    assert process_count([IntervalTarget(0.0, 5000)], cpu_count=16) == 5
    assert split_count(7, 3) == [3, 2, 2]


def test_percentiles_fusionnes_exacts() -> None:
    first = [1.0] * 900 + [100.0] * 100
    second = [1.0] * 100
    merged = merge([histogram_of(first), histogram_of(second)])
    exact = sorted(first + second)
    assert percentile_ms(merged, 0.95) == pytest.approx(exact[int(0.95 * len(exact)) - 1], rel=0.02)
    # moyenne des p95 par seconde : 50 ms, faux ; fusion : 100 ms
    assert percentile_ms(merged, 0.95) > 90


def test_goulot_local_mesure_directement() -> None:
    from omega_stress.application.pipeline.degraded_mode import is_local_bottleneck
    from omega_stress.domain.runs.models import IntervalSample

    def sample(**kw: int) -> IntervalSample:
        return IntervalSample(
            at_second=0,
            observed_rate_per_minute=600,
            p50_latency_ms=1,
            p95_latency_ms=1,
            p99_latency_ms=1,
            error_count=0,
            request_count=10,
            **kw,
        )

    # cible saturee : peu de requetes terminees, mais tout est parti a l'heure -> pas la faute
    # de la machine
    assert not is_local_bottleneck(sample(emitted_count=100), requested_rate_per_minute=6000)
    assert is_local_bottleneck(
        sample(emitted_count=100, late_emitted_count=30), requested_rate_per_minute=6000
    )
    assert is_local_bottleneck(
        sample(emitted_count=90, not_emitted_count=10), requested_rate_per_minute=6000
    )
    # ancien moteur (pas de comptes d'emission) : ancienne regle
    assert is_local_bottleneck(sample(), requested_rate_per_minute=6000)


def test_connexion_fermee_par_la_cible_rouverte_sans_erreur() -> None:
    """Correctif 2.0.0 : serveur HTTP/1.0 (ferme apres chaque reponse) et serveur qui coupe une
    connexion inactive (comme Apache apres 5 s) : fermetures normales, jamais des erreurs."""
    import socket

    from omega_stress.infrastructure.runner.open_loop.http1 import HeldConnection, parse_target

    class Http10(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Http10)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    raw = socket.socket()
    raw.bind(("127.0.0.1", 0))
    raw.listen()

    def idle_closer() -> None:  # repond une fois par connexion (keep-alive annonce), puis coupe
        while True:
            try:
                conn, _ = raw.accept()
            except OSError:
                return
            conn.recv(4096)
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
            time.sleep(0.05)
            conn.close()

    threading.Thread(target=idle_closer, daemon=True).start()

    async def go() -> list[int]:
        statuses = []
        for port in (server.server_address[1], raw.getsockname()[1]):
            held = HeldConnection(parse_target(f"http://127.0.0.1:{port}/", "t"), None)
            for _ in range(3):
                statuses.append(await held.get())
                await asyncio.sleep(0.2)
            await held.close()
        return statuses

    try:
        assert asyncio.run(go()) == [200] * 6
    finally:
        server.shutdown()
        raw.close()


def test_demarrage_depuis_l_interface_stderr_capture(fast_server: str, monkeypatch) -> None:
    """Correctif 2.0.0 (essai reel de l'auteur, 2026-11-21) : sous Textual, sys.stderr est une
    capture dont le descripteur vaut -1 ; multiprocessing echouait (« bad value(s) in
    fds_to_keep ») et aucun test ne partait depuis l'interface."""
    import sys

    class Capture:
        def write(self, text: str) -> int:
            return len(text)

        def flush(self) -> None:
            pass

        def fileno(self) -> int:
            return -1

    monkeypatch.setattr(sys, "stderr", Capture())
    monkeypatch.setattr(sys, "stdout", Capture())
    samples = _collect(
        OpenLoopLoadGenerator(processes=1), [IntervalTarget(10.0, 0)] * 2, fast_server
    )
    assert [s.emitted_count for s in samples] == [10, 10]
    assert isinstance(sys.stderr, Capture)  # la capture est remise en place apres le demarrage
