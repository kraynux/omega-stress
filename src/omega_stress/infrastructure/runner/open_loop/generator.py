# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Generateur de charge en boucle ouverte, multiprocessus (Phase 0 + Phase 1 du plan de charge
distribuee, STRESS/ETUDE_VERIFICATION_CODE_CHARGE_DISTRIBUEE.md §10, decision de l'auteur du
2026-11-21).

Implemente ports/load_runner.py::LoadRunner (meme contrat que httpx_load_generator.py : un
IntervalSample par seconde). L'emission ne tourne plus dans la boucle de l'interface : N processus
(worker.py), un par part de la charge, au plus coeurs - 1. Ce processus-ci ne fait que cadencer les
secondes, repartir le debit, et fusionner les comptes rendus (histogrammes additionnes : percentiles
exacts, jamais une moyenne de percentiles).

Le debit observe est celui des requetes TERMINEES par seconde reelle ; les requetes emises et celles
non emises (plafond en vol atteint) sont rendues a part, pour que l'ecran dise quand la machine ne
suit pas."""

from __future__ import annotations

import asyncio
import contextlib
import math
import multiprocessing
import os
import time
from collections import Counter
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.domain.load.histogram import Histogram, merge, percentile_ms
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.policies import (
    OPEN_LOOP_CONNECTIONS_PER_PROCESS,
    OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
    OPEN_LOOP_REQUESTS_PER_PROCESS,
    OPEN_LOOP_WORKER_REPORT_TIMEOUT_SECONDS,
    SAMPLE_INTERVAL_SECONDS,
)
from omega_stress.domain.runs.models import ErrorBreakdown, IntervalSample, SystemSnapshot
from omega_stress.infrastructure.probe.live_probe import LiveSystemSampler
from omega_stress.infrastructure.process_start import start_process
from omega_stress.infrastructure.runner.engine_params import (
    IntervalTarget,
    target_for_interval,
    total_intervals,
)
from omega_stress.infrastructure.runner.httpx_load_generator import USER_AGENT
from omega_stress.infrastructure.runner.open_loop.worker import ERROR_KEYS, worker_main
from omega_stress.ports.system_sampler import SystemSampler
from omega_stress.shared.i18n import _

_START_TIMEOUT_SECONDS = 30.0


def process_count(targets: list[IntervalTarget], cpu_count: int | None = None) -> int:
    """Processus d'emission necessaires pour le pic du plan, au plus coeurs - 1 (un coeur reste a
    l'interface)."""
    peak_rate = max((t.requests_per_second for t in targets), default=0.0)
    peak_connections = max((t.concurrency for t in targets), default=0)
    needed = max(
        1,
        math.ceil(peak_rate / OPEN_LOOP_REQUESTS_PER_PROCESS),
        math.ceil(peak_connections / OPEN_LOOP_CONNECTIONS_PER_PROCESS),
    )
    available = max(1, (cpu_count if cpu_count is not None else os.cpu_count() or 2) - 1)
    return min(needed, available)


def split_rate(rate: float, parts: int) -> list[float]:
    return [rate / parts] * parts


def split_count(total: int, parts: int) -> list[int]:
    base, extra = divmod(total, parts)
    return [base + (1 if index < extra else 0) for index in range(parts)]


def build_sample(
    index: int,
    target: IntervalTarget,
    reports: list[dict[str, Any]],
    duration: float,
    system: SystemSnapshot | None,
) -> IntervalSample:
    """Fusion des comptes rendus d'une seconde (processus locaux, ou workers distants en Phase 2) :
    histogrammes additionnes, compteurs sommes."""
    histogram: Histogram = merge(tuple(tuple(pair) for pair in r["histogram"]) for r in reports)
    errors: Counter[str] = Counter()
    for report in reports:
        errors.update(report["errors"])
    completed = sum(report["completed"] for report in reports)
    return IntervalSample(
        at_second=index * SAMPLE_INTERVAL_SECONDS,
        observed_rate_per_minute=completed * 60.0 / duration,
        p50_latency_ms=percentile_ms(histogram, 0.50),
        p95_latency_ms=percentile_ms(histogram, 0.95),
        p99_latency_ms=percentile_ms(histogram, 0.99),
        error_count=sum(errors.values()),
        request_count=completed,
        requested_rate_per_minute=(
            target.requests_per_second * 60.0 if target.requests_per_second > 0 else None
        ),
        active_connections=sum(report["active"] for report in reports),
        errors=ErrorBreakdown(**{key: errors.get(key, 0) for key in ERROR_KEYS}),
        system=system,
        emitted_count=sum(report["emitted"] for report in reports),
        not_emitted_count=sum(report["not_emitted"] for report in reports),
        late_emitted_count=sum(report["late"] for report in reports),
        latency_histogram=histogram,
    )


class OpenLoopLoadGenerator:
    def __init__(
        self,
        *,
        timeout_seconds: float = 10.0,
        system_sampler: SystemSampler | None = None,
        processes: int | None = None,
        inflight_cap: int = OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._system_sampler = system_sampler if system_sampler is not None else LiveSystemSampler()
        self._forced_processes = processes
        self._inflight_cap = inflight_cap
        self._context = multiprocessing.get_context("spawn")

    async def run(self, plan: LoadPlan, *, target_url: str) -> AsyncGenerator[IntervalSample, None]:
        targets = [target_for_interval(plan, index) for index in range(total_intervals(plan))]
        async for sample in self.stream(targets, target_url=target_url):
            yield sample

    async def stream(
        self, targets: list[IntervalTarget], *, target_url: str
    ) -> AsyncGenerator[IntervalSample, None]:
        """Execute une cible par seconde (separe de run() pour les essais de quelques secondes)."""
        await self._check_reachable(target_url)
        count = self._forced_processes or process_count(targets)
        pool = EmitterPool(self._context, count, target_url, self._timeout_seconds, self._inflight_cap)
        try:
            await pool.start()
            loop = asyncio.get_running_loop()
            started = loop.time()
            previous_end = time.monotonic()
            for index, target in enumerate(targets):
                tick_at = started + index * SAMPLE_INTERVAL_SECONDS
                delay = tick_at - loop.time()
                if delay > 0:
                    await asyncio.sleep(delay)
                pool.tick(
                    index,
                    split_rate(target.requests_per_second, count),
                    split_count(target.concurrency, count),
                )
                reports = await pool.reports(index)
                now = time.monotonic()
                duration = max(SAMPLE_INTERVAL_SECONDS, now - previous_end)
                previous_end = now
                yield self._sample(index, target, reports, duration)
        finally:
            await pool.stop()

    async def _check_reachable(self, target_url: str) -> None:
        """Comme httpx_load_generator.py : une cible injoignable des le depart ne produit
        aucune mesure."""
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds, headers={"User-Agent": USER_AGENT}
            ) as client:
                await client.get(target_url)
        except httpx.HTTPError as exc:
            raise RunnerFailureError(
                _("Cible {target_url!r} injoignable dès le départ : {exc}").format(
                    target_url=target_url, exc=exc
                )
            ) from exc

    def _sample(
        self, index: int, target: IntervalTarget, reports: list[dict[str, Any]], duration: float
    ) -> IntervalSample:
        return build_sample(index, target, reports, duration, self._system_sampler.sample())


class EmitterPool:
    """Les processus d'emission et leurs tuyaux ; jamais de lecture bloquante sur la boucle
    asyncio."""

    def __init__(
        self, context: Any, count: int, url: str, timeout: float, inflight_cap: int
    ) -> None:
        self._context = context
        self._count = count
        self._args = (url, timeout, inflight_cap, USER_AGENT)
        self._processes: list[Any] = []
        self._pipes: list[Any] = []
        self._queues: list[asyncio.Queue[tuple[Any, ...]]] = []

    @property
    def size(self) -> int:
        return self._count

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        for _index in range(self._count):
            parent, child = self._context.Pipe()
            process = self._context.Process(
                target=worker_main, args=(child, *self._args), daemon=True
            )
            start_process(process)
            child.close()
            queue: asyncio.Queue[tuple[Any, ...]] = asyncio.Queue()
            loop.add_reader(parent.fileno(), self._reader(parent, queue))
            self._processes.append(process)
            self._pipes.append(parent)
            self._queues.append(queue)
        for queue in self._queues:
            message = await asyncio.wait_for(self._next(queue, "ready"), _START_TIMEOUT_SECONDS)
            if message[0] != "ready":
                raise RunnerFailureError(_("Le moteur d'émission n'a pas démarré."))

    @staticmethod
    def _reader(pipe: Any, queue: asyncio.Queue[tuple[Any, ...]]) -> Any:
        def on_readable() -> None:
            try:
                while pipe.poll():
                    queue.put_nowait(pipe.recv())
            except (EOFError, OSError):
                queue.put_nowait(("gone",))

        return on_readable

    @staticmethod
    async def _next(queue: asyncio.Queue[tuple[Any, ...]], kind: str) -> tuple[Any, ...]:
        while True:
            message = await queue.get()
            if message[0] in (kind, "gone"):
                return message

    def tick(self, index: int, rates: list[float], connections: list[int]) -> None:
        for pipe, rate, held in zip(self._pipes, rates, connections, strict=True):
            try:
                pipe.send(("tick", index, rate, held))
            except (BrokenPipeError, OSError):
                continue

    async def reports(self, index: int) -> list[dict[str, Any]]:
        """Comptes rendus de la seconde `index`. Un processus muet ou disparu compte pour zero
        (mesure incomplete plutot qu'un run bloque)."""
        timeout = SAMPLE_INTERVAL_SECONDS + OPEN_LOOP_WORKER_REPORT_TIMEOUT_SECONDS
        results = await asyncio.gather(
            *(self._report(queue, index, timeout) for queue in self._queues)
        )
        return [report for report in results if report is not None]

    async def _report(
        self, queue: asyncio.Queue[tuple[Any, ...]], index: int, timeout: float
    ) -> dict[str, Any] | None:
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return None
            try:
                message = await asyncio.wait_for(self._next(queue, "report"), remaining)
            except asyncio.TimeoutError:
                return None
            if message[0] == "gone":
                return None
            if message[1] == index:
                report: dict[str, Any] = message[2]
                return report

    async def stop(self) -> None:
        loop = asyncio.get_running_loop()
        for pipe in self._pipes:
            with contextlib.suppress(BrokenPipeError, OSError):
                pipe.send(("stop",))
        for pipe in self._pipes:
            with contextlib.suppress(OSError, ValueError):
                loop.remove_reader(pipe.fileno())
        deadline = time.monotonic() + 3.0
        for process in self._processes:
            while process.is_alive() and time.monotonic() < deadline:
                await asyncio.sleep(0.05)
            if process.is_alive():
                process.terminate()
                process.join(1.0)
        for pipe in self._pipes:
            pipe.close()
