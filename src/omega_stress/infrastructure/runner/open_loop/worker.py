# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Processus d'emission en BOUCLE OUVERTE (Phase 0 du plan de charge distribuee, 2026-11-21).

Lance par generator.py (multiprocessing, methode « spawn »), un par part de la charge. Le parent
cadence le temps : a chaque seconde il envoie ("tick", debit, connexions) ; le processus emet
pendant 1 s, SANS attendre les reponses (chaque requete part a l'instant prevu t = debut + k /
debit), puis rend ses comptes ("report", ...) :

- latence mesuree depuis l'instant PREVU d'emission (correction de l'omission coordonnee : ce que
  vit un vrai client quand la cible ralentit) ;
- requete prevue alors que OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS requetes sont deja en vol : comptee «
  non emise », jamais retardee en silence ;
- Test connexions (lecture B) : N connexions TENUES (http1.HeldConnection), chacune envoie une
  requete toutes les CONNECTION_REQUEST_PERIOD_SECONDS, decalees.

Aucune sortie sur le terminal (l'interface Textual l'occupe) ; Ctrl+C est laisse au parent."""

from __future__ import annotations

import asyncio
import os
import signal
import ssl
import sys
import time
from collections import Counter
from typing import Any

from omega_stress.domain.load.histogram import bucket_of
from omega_stress.domain.load.policies import (
    CONNECTION_REQUEST_PERIOD_SECONDS,
    EMISSION_LATE_MS,
    OPEN_LOOP_POOL_CONNECTIONS_PER_PROCESS,
)
from omega_stress.infrastructure.runner.open_loop.http1 import HeldConnection, parse_target

ERROR_KEYS = ("timeout", "connection", "http_4xx", "http_5xx", "other")


def worker_main(
    conn: Any, target_url: str, timeout_seconds: float, inflight_cap: int, user_agent: str
) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    devnull = open(os.devnull, "w")  # noqa: SIM115 - garde jusqu'a la fin du processus
    sys.stdout = sys.stderr = devnull
    try:
        asyncio.run(_Worker(conn, target_url, timeout_seconds, inflight_cap, user_agent).serve())
    finally:
        conn.close()


class _Worker:
    def __init__(
        self, conn: Any, url: str, timeout: float, inflight_cap: int, user_agent: str
    ) -> None:
        self._conn = conn
        self._url = url
        self._timeout = timeout
        self._cap = inflight_cap
        self._user_agent = user_agent
        self._commands: asyncio.Queue[tuple[Any, ...]] = asyncio.Queue()
        self._inflight = 0
        self._tasks: set[asyncio.Task[None]] = set()
        self._reset_counts()
        self._connections: list[asyncio.Task[None]] = []
        self._open_connections = 0
        self._carry = 0.0
        self._idle: list[HeldConnection] = []
        self._pool_size = 0
        self._freed = asyncio.Event()
        self._target = parse_target(url, user_agent)
        self._ssl = ssl.create_default_context() if self._target.tls else None

    def _reset_counts(self) -> None:
        self._completed = 0
        self._emitted = 0
        self._not_emitted = 0
        self._late = 0
        self._errors: Counter[str] = Counter()
        self._histogram: Counter[int] = Counter()

    async def serve(self) -> None:
        loop = asyncio.get_running_loop()
        loop.add_reader(self._conn.fileno(), self._on_command)
        self._conn.send(("ready",))
        while True:
            command = await self._commands.get()
            if command[0] == "stop":
                break
            if command[0] == "tick":
                _, index, rate, connections = command
                await self._tick(index, rate, connections)
        for task in list(self._tasks) + self._connections:
            task.cancel()
        await asyncio.gather(*self._tasks, *self._connections, return_exceptions=True)
        for connection in self._idle:
            await connection.close()
        loop.remove_reader(self._conn.fileno())

    def _on_command(self) -> None:
        try:
            while self._conn.poll():
                self._commands.put_nowait(self._conn.recv())
        except (EOFError, OSError):
            self._commands.put_nowait(("stop",))

    async def _tick(self, index: int, rate: float, connections: int) -> None:
        loop = asyncio.get_running_loop()
        started = loop.time()
        self._resize_connections(connections)
        if rate > 0:
            # partie fractionnaire du debit reportee d'une seconde a l'autre : la moyenne est exacte
            self._carry += rate
            count = int(self._carry)
            self._carry -= count
            for k in range(count):
                due = started + k / rate
                delay = due - loop.time()
                if delay > 0:
                    await asyncio.sleep(delay)
                self._launch(due)
        remaining = started + 1.0 - loop.time()
        if remaining > 0:
            await asyncio.sleep(remaining)
        self._report(index)

    def _launch(self, due: float) -> None:
        if self._inflight >= self._cap:
            self._not_emitted += 1
            return
        self._inflight += 1
        self._emitted += 1
        if (asyncio.get_running_loop().time() - due) * 1000 > EMISSION_LATE_MS:
            self._late += 1
        task = asyncio.ensure_future(self._request(due))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _request(self, due: float) -> None:
        """Requete sur une connexion de la reserve (client HTTP/1.1 leger, 2026-11-21 : httpx
        coutait ~6-7 ms de CPU par requete, soit ~150 req/s au plus par processus)."""
        category: str | None = None
        connection: HeldConnection | None = None
        try:
            connection = await self._borrow()
            status = await asyncio.wait_for(connection.get(), self._timeout)
            category = _status_category(status)
        except asyncio.TimeoutError:
            category = "timeout"
        except (OSError, ValueError, IndexError, asyncio.IncompleteReadError, ssl.SSLError):
            category = "connection"
        except Exception:  # noqa: BLE001 - une requete ratee ne doit jamais arreter l'emission
            category = "other"
        finally:
            self._inflight -= 1
            if connection is not None:
                await self._give_back(connection, healthy=category in (None, "http_4xx", "http_5xx"))
        self._record(due, category)

    async def _borrow(self) -> HeldConnection:
        while True:
            if self._idle:
                return self._idle.pop()
            if self._pool_size < OPEN_LOOP_POOL_CONNECTIONS_PER_PROCESS:
                self._pool_size += 1
                return HeldConnection(self._target, self._ssl)  # ouverte au premier get()
            self._freed.clear()
            await self._freed.wait()

    async def _give_back(self, connection: HeldConnection, *, healthy: bool) -> None:
        if healthy and connection.is_open:
            self._idle.append(connection)
        else:
            await connection.close()
            self._pool_size -= 1
        self._freed.set()

    def _record(self, due: float, category: str | None) -> None:
        latency_ms = (asyncio.get_running_loop().time() - due) * 1000
        self._completed += 1
        self._histogram[bucket_of(latency_ms)] += 1
        if category is not None:
            self._errors[category] += 1

    # ---- Test connexions, lecture B
    # --------------------------------------------------------------------------

    def _resize_connections(self, wanted: int) -> None:
        self._connections = [task for task in self._connections if not task.done()]
        while len(self._connections) < wanted:
            slot = len(self._connections)
            self._connections.append(asyncio.ensure_future(self._hold(slot, wanted)))
        while len(self._connections) > wanted:
            self._connections.pop().cancel()

    async def _hold(self, slot: int, total: int) -> None:
        loop = asyncio.get_running_loop()
        period = CONNECTION_REQUEST_PERIOD_SECONDS
        due = loop.time() + period * (
            slot / max(1, total)
        )  # decalage : requetes etalees sur la periode
        connection = HeldConnection(self._target, self._ssl)
        counted = False
        try:
            while True:
                if not counted:
                    try:
                        await asyncio.wait_for(connection.open(), self._timeout)
                        counted = True
                        self._open_connections += 1
                    except (OSError, asyncio.TimeoutError, ssl.SSLError):
                        self._record(loop.time(), "connection")
                        await asyncio.sleep(1.0)
                        continue
                delay = due - loop.time()
                if delay > 0:
                    await asyncio.sleep(delay)
                self._emitted += 1
                category: str | None
                try:
                    category = _status_category(
                        await asyncio.wait_for(connection.get(), self._timeout)
                    )
                except asyncio.TimeoutError:
                    category = "timeout"
                except (OSError, ValueError, IndexError, asyncio.IncompleteReadError, ssl.SSLError):
                    category = "connection"
                self._record(due, category)
                if category in ("timeout", "connection") or not connection.is_open:
                    await connection.close()
                    if counted:
                        counted = False
                        self._open_connections -= 1
                due += period
        finally:
            if counted:
                self._open_connections -= 1
            await connection.close()

    # ---- comptes
    # ----------------------------------------------------------------------------------------------

    def _report(self, index: int) -> None:
        self._conn.send(
            (
                "report",
                index,
                {
                    "completed": self._completed,
                    "emitted": self._emitted,
                    "not_emitted": self._not_emitted,
                    "late": self._late,
                    "errors": {key: self._errors.get(key, 0) for key in ERROR_KEYS},
                    "histogram": tuple(sorted(self._histogram.items())),
                    "active": self._inflight + self._open_connections,
                    "at": time.monotonic(),
                },
            )
        )
        self._reset_counts()


def _status_category(status: int) -> str | None:
    if status >= 500:
        return "http_5xx"
    if status >= 400:
        return "http_4xx"
    return None
