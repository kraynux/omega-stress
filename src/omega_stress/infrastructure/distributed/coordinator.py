# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Coordinateur de charge distribuee (Phase 2, 2026-11-21).

`DistributedLoadGenerator` implemente ports/load_runner.py::LoadRunner, comme le moteur local :
le pipeline (gardes, pre-check, historique, exports, rampes, profils D1-D6) est reutilise tel quel.
Chaque seconde, chaque worker recoit sa part (debit, connexions), emet avec ses propres processus
(moteur 2.0) et renvoie comptes + histogramme ; les comptes sont fusionnes ici (histogrammes
additionnes : percentiles exacts sur l'ensemble des machines).

Le coordinateur n'emet pas lui-meme (la machine qui mesure n'est pas celle qui charge, plan §6.1).
Un worker qui refuse l'armement est ecarte et signale ; un worker perdu en cours de route est
signale (« worker K perdu a la seconde J ») et le run continue sans lui."""

from __future__ import annotations

import asyncio
import contextlib
import math
import multiprocessing
import os
import re
import shlex
import socket
import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.domain.distributed.policies import (
    APPROVAL_NEEDED,
    DISTRIBUTED_PORT,
    allocate,
    split_whole,
)
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.policies import (
    OPEN_LOOP_CONNECTIONS_PER_PROCESS,
    OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
    OPEN_LOOP_REQUESTS_PER_PROCESS,
    OPEN_LOOP_WORKER_REPORT_TIMEOUT_SECONDS,
    SAMPLE_INTERVAL_SECONDS,
)
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.infrastructure.distributed.identity import (
    ensure_coordinator_identity,
    fingerprint_of,
    server_context,
)
from omega_stress.infrastructure.distributed.protocol import ProtocolError, receive, send
from omega_stress.infrastructure.distributed.store import DistributedStore
from omega_stress.infrastructure.distributed.worker_agent import default_capacity_rps, merge_reports
from omega_stress.infrastructure.probe.live_probe import LiveSystemSampler
from omega_stress.infrastructure.runner.engine_params import (
    IntervalTarget,
    target_for_interval,
    total_intervals,
)
from omega_stress.infrastructure.runner.open_loop.generator import (
    EmitterPool,
    build_sample,
    split_count,
    split_rate,
)
from omega_stress.ports.system_sampler import SystemSampler
from omega_stress.shared.i18n import _

DEFAULT_PORT = DISTRIBUTED_PORT
REMOTE_PATH = "export PATH=/usr/local/bin:/usr/bin:/bin:$PATH; "
"""En tete de chaque commande lancee par SSH : sans terminal, certaines machines (Archcraft,
constate par omega-connect le 2026-11-11) n'ont presque rien dans le PATH, et omega-stress.sh a
besoin de dirname."""
_JOIN_TIMEOUT_SECONDS = 120.0
_ARM_TIMEOUT_SECONDS = 60.0


@dataclass
class _Session:
    worker_id: str
    name: str
    capacity_rps: float
    cpus: int
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    inbox: asyncio.Queue[dict[str, Any]] = field(default_factory=asyncio.Queue)
    closed: asyncio.Event = field(default_factory=asyncio.Event)
    lost: bool = False

    async def pump(self) -> None:
        try:
            while True:
                await self.inbox.put(await receive(self.reader))
        except (ProtocolError, ConnectionError, OSError):
            pass
        finally:
            self.lost = True
            await self.inbox.put({"type": "gone"})
            self.closed.set()

    async def expect(self, kinds: tuple[str, ...], timeout: float) -> dict[str, Any] | None:
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return None
            try:
                message = await asyncio.wait_for(self.inbox.get(), remaining)
            except asyncio.TimeoutError:
                return None
            if message["type"] == "gone":
                return None
            if message["type"] in kinds:
                return message


class Coordinator:
    """Serveur TLS du canal de controle : appairages et arrivee des workers."""

    def __init__(self, store: DistributedStore, port: int, host: str = "0.0.0.0") -> None:
        self._store = store
        self._port = port
        self._host = host
        self._server: asyncio.Server | None = None
        self.sessions: list[_Session] = []
        self.paired: list[str] = []
        self._changed = asyncio.Event()
        self._tasks: set[asyncio.Task[None]] = set()
        cert, _key = ensure_coordinator_identity(store.directory)
        self.fingerprint = fingerprint_of(cert)

    @property
    def port(self) -> int:
        if self._server is not None and self._server.sockets:
            return int(self._server.sockets[0].getsockname()[1])
        return self._port

    async def start(self) -> None:
        cert, key = ensure_coordinator_identity(self._store.directory)
        self._server = await asyncio.start_server(
            self._on_connect,
            self._host,
            self._port,
            ssl=server_context(cert, key),
            limit=8 * 1024 * 1024,
        )

    async def stop(self) -> None:
        for session in self.sessions:
            session.writer.close()
        if self._server is not None:
            self._server.close()
            with contextlib.suppress(Exception):
                await asyncio.wait_for(self._server.wait_closed(), 5)
        for task in list(self._tasks):
            task.cancel()

    async def _on_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            message = await receive(reader, 15.0)
        except (ProtocolError, asyncio.TimeoutError, ConnectionError, OSError):
            writer.close()
            return
        if message["type"] == "pair":
            if self._store.consume_pairing_code(str(message.get("code", ""))):
                name = str(message.get("name", "worker"))
                worker_id, secret = self._store.add_worker(name)
                await send(writer, {"type": "paired", "worker_id": worker_id, "secret": secret})
                self.paired.append(name)
                self._changed.set()
            else:
                await send(
                    writer, {"type": "rejected", "reason": "invalid or expired pairing code"}
                )
            writer.close()
            return
        if message["type"] == "hello":
            known_name = self._store.check_worker(
                str(message.get("worker_id", "")), str(message.get("secret", ""))
            )
            if known_name is None:
                await send(writer, {"type": "rejected", "reason": "unknown worker or bad secret"})
                writer.close()
                return
            session = _Session(
                worker_id=str(message["worker_id"]),
                name=known_name,
                capacity_rps=max(1.0, float(message.get("capacity_rps", 1.0))),
                cpus=max(1, int(message.get("cpus", 1))),
                reader=reader,
                writer=writer,
            )
            await send(writer, {"type": "welcome"})
            self.sessions.append(session)
            task = asyncio.ensure_future(session.pump())
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            self._changed.set()
            await session.closed.wait()
            return
        writer.close()

    async def wait_for(self, predicate: Callable[[], bool], timeout: float) -> bool:
        deadline = asyncio.get_running_loop().time() + timeout
        while not predicate():
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return False
            self._changed.clear()
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self._changed.wait(), remaining)
        return True


class _LocalParticipant:
    """« Cette machine » quand elle charge aussi (case cochee) : ses propres processus d'emission,
    sans canal reseau ni autorisation (c'est la machine de celui qui decide)."""

    @property
    def name(self) -> str:
        return _("cette machine")

    lost = False

    def __init__(self, target_url: str, processes: int) -> None:
        self.pool = EmitterPool(
            multiprocessing.get_context("spawn"),
            processes,
            target_url,
            10.0,
            OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
        )


Approver = Callable[[str, str], Awaitable[bool]]
"""(nom de la machine qui aide, cible « schema://hote[:port] ») -> accord du proprietaire."""


_REFUSALS = (
    (re.compile(r"^no worker authorization"), lambda m: _("aucune autorisation sur cette machine")),
    (
        re.compile(r"^coordinator not accepted"),
        lambda m: _("ce pilote n'est pas accepté par cette machine"),
    ),
    (
        re.compile(r"^duration above this worker's limit \((\d+) min\)"),
        lambda m: _("durée au-delà de sa limite ({value} min)").format(value=m.group(1)),
    ),
    (
        re.compile(r"^rate above this worker's limit \((\d+) req/min\)"),
        lambda m: _("débit au-delà de sa limite ({value} req/min)").format(value=m.group(1)),
    ),
    (
        re.compile(r"^connections above this worker's limit \((\d+)\)"),
        lambda m: _("connexions au-delà de sa limite ({value})").format(value=m.group(1)),
    ),
)


def refusal_text(reason: str) -> str:
    """Raison de refus d'une machine qui aide (anglais technique dans le protocole) dans la langue
    de l'interface ; une raison inconnue (version plus recente) est montree telle quelle."""
    for pattern, text in _REFUSALS:
        match = pattern.match(reason)
        if match:
            return text(match)
    return reason


def local_address_towards(host: str) -> str:
    """Adresse de CETTE machine telle que la voit `host` (route choisie par le systeme) : le pilote
    la donne a chaque machine qui aide, plus de --annonce a taper."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.connect((host, 9))  # UDP : rien n'est envoye, seule la route est calculee
        return str(probe.getsockname()[0])


class DistributedLoadGenerator:
    """Pilote : `machines` = machines qui aident enregistrees (lancees par SSH a chaque test),
    `pulled_workers` = machines qui rejoignent d'elles-memes (`worker rejoindre`, ligne de
    commande), `include_local` = cette machine charge aussi."""

    def __init__(
        self,
        store: DistributedStore,
        *,
        port: int = DEFAULT_PORT,
        machines: tuple[str, ...] = (),
        pulled_workers: int = 0,
        include_local: bool = False,
        ssh_targets: tuple[str, ...] = (),
        announce: str = "",
        notify: Callable[[str], None] = print,
        approve: Approver | None = None,
        system_sampler: SystemSampler | None = None,
        join_timeout_seconds: float = _JOIN_TIMEOUT_SECONDS,
        expected_workers: int | None = None,
    ) -> None:
        self._store = store
        self._port = port
        self._machines = machines
        self._pulled = pulled_workers if expected_workers is None else expected_workers
        self._include_local = include_local
        self._ssh = ssh_targets
        self._announce = announce
        self._notify = notify
        self._approve = approve
        self._system_sampler = system_sampler if system_sampler is not None else LiveSystemSampler()
        self._join_timeout = join_timeout_seconds
        self.coordinator: Coordinator | None = None
        self._participation: dict[str, dict[str, Any]] = {}
        """Bilan par machine (retour de l'auteur, 2026-11-21 : « aucun moyen de savoir si craftdark
        a participe ») : etat (rejointe, prete, ecartee, perdue) et requetes emises / terminees /
        erreurs."""

    def _note(self, name: str, status: str, detail: str = "") -> None:
        entry = self._participation.setdefault(
            name, {"status": status, "emitted": 0, "completed": 0, "errors": 0, "detail": ""}
        )
        entry["status"], entry["detail"] = status, detail or entry["detail"]

    def _count(self, name: str, report: dict[str, Any]) -> None:
        entry = self._participation.get(name)
        if entry is not None:
            entry["emitted"] += int(report.get("emitted", 0))
            entry["completed"] += int(report.get("completed", 0))
            entry["errors"] += sum(int(v) for v in report.get("errors", {}).values())

    def participation_summary(self) -> str:
        """Une ligne par machine, gardee avec le run (detail du run, exports)."""
        parts = []
        for name, entry in self._participation.items():
            if entry["status"] == "excluded":
                parts.append(
                    _("{machine} : écartée ({reason})").format(machine=name, reason=entry["detail"])
                )
                continue
            text = _(
                "{machine} : {emitted} requêtes émises, {completed} terminées, {errors} erreur(s)"
            ).format(
                machine=name,
                emitted=entry["emitted"],
                completed=entry["completed"],
                errors=entry["errors"],
            )
            if entry["status"] == "lost":
                text += " " + _("(perdue à la seconde {second})").format(second=entry["detail"])
            parts.append(text)
        return (_("Charge distribuée — ") + " ; ".join(parts)) if parts else ""

    @property
    def _expected(self) -> int:
        return len(self._machines) + self._pulled + len(self._ssh)

    async def run(self, plan: LoadPlan, *, target_url: str) -> AsyncGenerator[IntervalSample, None]:
        targets = [target_for_interval(plan, index) for index in range(total_intervals(plan))]
        async for sample in self.stream(
            targets, target_url=target_url, duration_minutes=plan.duration.minutes
        ):
            yield sample

    async def stream(
        self, targets: list[IntervalTarget], *, target_url: str, duration_minutes: float
    ) -> AsyncGenerator[IntervalSample, None]:
        if self._expected == 0 and not self._include_local:
            raise RunnerFailureError(_("Aucune machine pour charger la cible."))
        coordinator = Coordinator(self._store, self._port)
        self.coordinator = coordinator
        await coordinator.start()
        ssh_processes: list[asyncio.subprocess.Process] = []
        sessions: list[_Session] = []
        local: _LocalParticipant | None = None
        try:
            ssh_processes = await self._push_workers(coordinator)
            if self._expected:
                self._notify(
                    _("En attente de {count} machine(s) qui aident…").format(count=self._expected)
                )
                await coordinator.wait_for(
                    lambda: len(coordinator.sessions) >= self._expected, self._join_timeout
                )
            sessions = list(coordinator.sessions)
            if len(sessions) < self._expected:
                missing = self._missing_names(sessions)
                raise RunnerFailureError(
                    _("{joined} machine(s) sur {expected} ont rejoint le pilote.").format(
                        joined=len(sessions), expected=self._expected
                    )
                    + (
                        " " + _("Absentes : {names}.").format(names=", ".join(missing))
                        if missing
                        else ""
                    )
                )
            for session in sessions:
                self._note(session.name, "joined")
                self._notify(_("{machine} a rejoint le pilote.").format(machine=session.name))
            peak_rps = max((t.requests_per_second for t in targets), default=0.0)
            peak_connections = max((t.concurrency for t in targets), default=0)
            local_capacity = default_capacity_rps() if self._include_local else 0.0
            sessions, weights, local_weight = await self._arm(
                sessions, peak_rps, peak_connections, local_capacity, target_url, duration_minutes
            )
            if local_weight > 0:
                local = _LocalParticipant(
                    target_url,
                    self._processes(
                        peak_rps * local_weight,
                        round(peak_connections * local_weight),
                        os.cpu_count() or 1,
                    ),
                )
                await local.pool.start()
                self._note(local.name, "armed")
            ready = [n for n, e in self._participation.items() if e["status"] == "armed"]
            self._notify(
                _("Départ — machines qui chargent : {machines}.").format(machines=", ".join(ready))
            )
            loop = asyncio.get_running_loop()
            started = loop.time()
            previous_end = time.monotonic()
            for index, target in enumerate(targets):
                delay = started + index * SAMPLE_INTERVAL_SECONDS - loop.time()
                if delay > 0:
                    await asyncio.sleep(delay)
                live = [(s, w) for s, w in zip(sessions, weights, strict=True) if not s.lost]
                shares = [w for _, w in live] + ([local_weight] if local else [])
                connections = split_whole(target.concurrency, shares)
                for (session, weight), held in zip(live, connections, strict=False):
                    with contextlib.suppress(ConnectionError, OSError):
                        await send(
                            session.writer,
                            {
                                "type": "tick",
                                "index": index,
                                "rps": target.requests_per_second * weight,
                                "connections": held,
                            },
                        )
                waits = [self._report(s, index) for s, _ in live]
                if local is not None:
                    local.pool.tick(
                        index,
                        split_rate(target.requests_per_second * local_weight, local.pool.size),
                        split_count(connections[-1], local.pool.size),
                    )
                    waits.append(self._local_report(local, index))
                reports = await asyncio.gather(*waits)
                if local is not None and reports and reports[-1] is not None:
                    self._count(local.name, reports[-1])
                for (session, _weight), report in zip(live, reports, strict=False):
                    if report is not None:
                        self._count(session.name, report)
                    if report is None and not getattr(session, "announced", False):
                        session.announced = True  # type: ignore[attr-defined]
                        session.lost = True
                        self._note(session.name, "lost", str(index))
                        self._notify(
                            _(
                                "Machine {machine} perdue à la seconde {second} : mesure "
                                "incomplète à partir de là."
                            ).format(machine=session.name, second=index)
                        )
                now = time.monotonic()
                duration = max(SAMPLE_INTERVAL_SECONDS, now - previous_end)
                previous_end = now
                yield build_sample(
                    index,
                    target,
                    [r for r in reports if r is not None],
                    duration,
                    self._system_sampler.sample(),
                )
        finally:
            summary = self.participation_summary()
            if summary:
                self._notify(summary)
            for session in sessions:
                with contextlib.suppress(ConnectionError, OSError):
                    await send(session.writer, {"type": "end"})
            for session in sessions:
                if not session.lost:
                    await session.expect(("done",), 5.0)
            if local is not None:
                await local.pool.stop()
            await coordinator.stop()
            for process in ssh_processes:
                with contextlib.suppress(ProcessLookupError):
                    process.terminate()

    @staticmethod
    async def _local_report(local: _LocalParticipant, index: int) -> dict[str, Any]:
        return merge_reports(await local.pool.reports(index))

    @staticmethod
    def _processes(share_rps: float, connections: int, cpus: int) -> int:
        return min(
            max(1, cpus - 1),
            max(
                1,
                math.ceil(share_rps / OPEN_LOOP_REQUESTS_PER_PROCESS),
                math.ceil(connections / OPEN_LOOP_CONNECTIONS_PER_PROCESS),
            ),
        )

    def _missing_names(self, sessions: list[_Session]) -> list[str]:
        joined = {s.worker_id for s in sessions}
        known = self._store.workers()
        return [known.get(m, {}).get("name", m) for m in self._machines if m not in joined]

    async def _arm(
        self,
        sessions: list[_Session],
        peak_rps: float,
        peak_connections: int,
        local_capacity: float,
        target_url: str,
        duration_minutes: float,
    ) -> tuple[list[_Session], list[float], float]:
        capacities = [s.capacity_rps for s in sessions] + (
            [local_capacity] if local_capacity else []
        )
        shares = allocate(peak_rps, capacities)
        if shares is None:
            raise RunnerFailureError(
                _(
                    "Débit demandé ({asked} req/min) au-delà de la capacité des machines "
                    "({most} req/min au plus) : test refusé."
                ).format(asked=f"{peak_rps * 60:.0f}", most=f"{sum(capacities) * 60:.0f}")
            )
        total_capacity = sum(capacities)
        weights = (
            [share / peak_rps for share in shares]
            if peak_rps > 0
            else [c / total_capacity for c in capacities]
        )
        held = split_whole(peak_connections, weights)
        campaign = uuid.uuid4().hex[:12]

        async def arm_one(session: _Session, weight: float, connections: int) -> bool:
            message = {
                "type": "arm",
                "campaign": campaign,
                "target_url": target_url,
                "duration_minutes": duration_minutes,
                "peak_rpm": peak_rps * weight * 60,
                "peak_connections": connections,
                "processes": self._processes(peak_rps * weight, connections, session.cpus),
            }
            for _attempt in range(2):
                await send(session.writer, message)
                answer = await session.expect(("armed", "refused"), _ARM_TIMEOUT_SECONDS)
                if answer is not None and answer["type"] == "armed":
                    self._note(session.name, "armed")
                    return True
                reason = (
                    refusal_text(str(answer.get("reason", "?"))) if answer else _("pas de réponse")
                )
                if reason.startswith(APPROVAL_NEEDED) and _attempt == 0:
                    origin = reason[len(APPROVAL_NEEDED) :]
                    if await self._ask_owner(session, origin):
                        continue
                    reason = _("cible {target} non autorisée sur cette machine").format(
                        target=origin
                    )
                self._note(session.name, "excluded", reason)
                self._notify(
                    _("Machine {machine} écartée : {reason}").format(
                        machine=session.name, reason=reason
                    )
                )
                return False
            return False

        armed_flags = [
            await arm_one(s, w, c) for s, w, c in zip(sessions, weights, held, strict=False)
        ]
        armed = [
            (s, w)
            for (s, w), ok in zip(zip(sessions, weights, strict=False), armed_flags, strict=True)
            if ok
        ]
        local_weight = weights[-1] if local_capacity else 0.0
        if not armed and not local_weight:
            raise RunnerFailureError(_("Aucune machine n'a accepté le test."))
        total = sum(w for _, w in armed) + local_weight
        if len(armed) < len(sessions):
            self._notify(
                _("Part des machines écartées redistribuée aux autres, dans leurs limites.")
            )
        return [s for s, _ in armed], [w / total for _, w in armed], local_weight / total

    async def _ask_owner(self, session: _Session, origin: str) -> bool:
        """Accord « Demander » : la question est posee ici ; la reponse est ecrite SUR la machine
        qui
        aide, sous le compte de son proprietaire, par la cle SSH qu'il a acceptee."""
        record = self._store.workers().get(session.worker_id, {})
        if self._approve is None or not record.get("ssh") or not record.get("path"):
            return False
        if not await self._approve(session.name, origin):
            return False
        command = (
            REMOTE_PATH
            + f"cd {shlex.quote(record['path'])} && ./omega-stress.sh worker autoriser "
            f"--ajouter-cible {shlex.quote(origin)}"
        )
        process = await asyncio.create_subprocess_exec(
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            record["ssh"],
            command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        return await process.wait() == 0

    async def _report(self, session: _Session, index: int) -> dict[str, Any] | None:
        timeout = SAMPLE_INTERVAL_SECONDS + OPEN_LOOP_WORKER_REPORT_TIMEOUT_SECONDS
        while True:
            message = await session.expect(("report",), timeout)
            if message is None:
                return None
            if int(message.get("index", -1)) == index:
                data: dict[str, Any] = message["data"]
                return data

    async def _push_workers(self, coordinator: Coordinator) -> list[asyncio.subprocess.Process]:
        """Lance `worker rejoindre … --une-fois` par SSH : machines enregistrees (parcours simple :
        adresse du pilote trouvee seule, pilote reconnu a son empreinte) et --ssh (ligne de
        commande, avec --annonce)."""
        launches: list[tuple[str, str, str]] = []  # (ssh, dossier, adresse du pilote)
        known = self._store.workers()
        for worker_id in self._machines:
            record = known.get(worker_id)
            if record is None or not record.get("ssh") or not record.get("path"):
                raise RunnerFailureError(
                    _("Machine inconnue ou sans accès SSH : {machine}").format(machine=worker_id)
                )
            host = record["ssh"].rpartition("@")[2]
            try:
                address = local_address_towards(host)
            except OSError as error:
                raise RunnerFailureError(
                    _("{machine} injoignable : {error}").format(
                        machine=record.get("name", host), error=error
                    )
                ) from error
            launches.append((record["ssh"], record["path"], address))
        if self._ssh and not self._announce:
            raise RunnerFailureError(_("Mode poussé : --annonce <adresse du coordinateur> requis."))
        for target in self._ssh:
            host, _sep, path = target.partition(":")
            launches.append((host, path, self._announce))
        log_dir = self._store.directory
        log_dir.mkdir(parents=True, exist_ok=True)
        processes = []
        for ssh, path, address in launches:
            command = (
                REMOTE_PATH
                + f"cd {shlex.quote(path)} && ./omega-stress.sh worker rejoindre "
                f"{shlex.quote(f'{address}:{coordinator.port}')} --pilote "
                f"{coordinator.fingerprint} --une-fois"
            )
            log_path = Path(log_dir / f"ssh-{ssh.replace('@', '_')}.log")
            log = os.fdopen(os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600), "ab")
            processes.append(
                await asyncio.create_subprocess_exec(
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    ssh,
                    command,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=log,
                    stderr=log,
                )
            )
            log.close()  # le sous-processus garde sa propre copie du descripteur
        return processes
