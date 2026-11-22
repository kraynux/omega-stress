# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Worker de charge distribuee (Phase 2, 2026-11-21) : `omega-stress worker rejoindre`.

Le worker COMPOSE vers le coordinateur (mode tire ; le mode pousse lance la meme commande par
SSH) : aucune ecoute sur le worker. Chaine de gardes appliquee ICI, par le worker, quoi que
demande le coordinateur (plan §9.2) : empreinte du coordinateur epinglee, autorisation du
proprietaire (coordinateur accepte, cible permise, duree et debit maximum) verifiee a
l'armement, debit et connexions bridés a chaque seconde."""

from __future__ import annotations

import asyncio
import multiprocessing
import os
import socket
from collections.abc import Callable
from typing import Any

from omega_stress.domain.distributed.policies import refusal_reason
from omega_stress.domain.load.policies import (
    OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
    OPEN_LOOP_REQUESTS_PER_PROCESS,
)
from omega_stress.infrastructure.distributed.identity import client_context, peer_fingerprint
from omega_stress.infrastructure.distributed.protocol import ProtocolError, receive, send
from omega_stress.infrastructure.distributed.store import DistributedStore
from omega_stress.infrastructure.runner.open_loop.generator import (
    EmitterPool,
    split_count,
    split_rate,
)

_TIMEOUT_SECONDS = 10.0
_CONNECT_TIMEOUT_SECONDS = 15.0
_RETRY_SECONDS = 2.0


def split_address(address: str) -> tuple[str, int]:
    host, _, port = address.rpartition(":")
    if not host or not port.isdigit():
        raise ValueError(f"address must be host:port, got {address!r}")
    return host.strip("[]"), int(port)


def default_capacity_rps() -> float:
    """Capacite annoncee au coordinateur : estimation par coeurs (mesure du 2026-11-21 :
    ~1 000 req/s
    par processus d'emission, un coeur laisse libre). Le calibrage local l'affinera."""
    return max(1, (os.cpu_count() or 2) - 1) * OPEN_LOOP_REQUESTS_PER_PROCESS


async def pair(store: DistributedStore, address: str, fingerprint: str, code: str) -> str:
    """Appairage : verifie l'empreinte du coordinateur, remet le code a usage unique, garde
    le secret
    recu, et ajoute le coordinateur aux coordinateurs acceptes de l'autorisation (si elle existe :
    l'appairage est fait par le proprietaire, sur sa machine)."""
    host, port = split_address(address)
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port, ssl=client_context()), _CONNECT_TIMEOUT_SECONDS
    )
    try:
        actual = peer_fingerprint(writer.get_extra_info("ssl_object"))
        if actual != fingerprint.lower().replace(":", ""):
            raise ProtocolError("coordinator fingerprint does not match")
        await send(writer, {"type": "pair", "code": code, "name": socket.gethostname()})
        answer = await receive(reader, _TIMEOUT_SECONDS)
        if answer["type"] != "paired":
            raise ProtocolError(str(answer.get("reason", "pairing refused")))
        store.save_coordinator(address, actual, str(answer["worker_id"]), str(answer["secret"]))
        store.accept_coordinator(actual)
        return actual
    finally:
        writer.close()


async def join(
    store: DistributedStore,
    address: str,
    *,
    version: str,
    once: bool,
    log: Callable[[str], None],
    capacity_rps: float | None = None,
    wait_seconds: float | None = None,
    fingerprint: str | None = None,
) -> int:
    """Rejoint le coordinateur et sert ses campagnes. Rend 0, ou 1 si le coordinateur est refuse.

    Le coordinateur n'ecoute que pendant un run distribue : tant qu'il ne repond pas, le worker
    reessaie toutes les _RETRY_SECONDS (indefiniment, ou wait_seconds au plus)."""
    record = store.coordinator_for(address, fingerprint)
    if record is None:
        log(f"not paired with {address} (omega-stress worker appairer)")
        return 1
    host, port = split_address(address)
    loop = asyncio.get_running_loop()
    deadline = None if wait_seconds is None else loop.time() + wait_seconds
    waiting_said = False
    while True:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port, ssl=client_context(), limit=8 * 1024 * 1024),
                _CONNECT_TIMEOUT_SECONDS,
            )
            break
        except (OSError, asyncio.TimeoutError):
            if deadline is not None and loop.time() >= deadline:
                raise
            if not waiting_said:
                log(f"waiting for the coordinator {address}…")
                waiting_said = True
            await asyncio.sleep(_RETRY_SECONDS)
    pool: EmitterPool | None = None
    try:
        fingerprint = peer_fingerprint(writer.get_extra_info("ssl_object"))
        if fingerprint != record["fingerprint"]:
            log("coordinator fingerprint changed: refused")
            return 1
        await send(
            writer,
            {
                "type": "hello",
                "worker_id": record["worker_id"],
                "secret": record["secret"],
                "version": version,
                "cpus": os.cpu_count() or 1,
                "capacity_rps": capacity_rps or default_capacity_rps(),
            },
        )
        answer = await receive(reader, _TIMEOUT_SECONDS)
        if answer["type"] != "welcome":
            log(f"rejected by coordinator: {answer.get('reason', '?')}")
            return 1
        log(f"joined {address}")
        limits: dict[str, Any] = {}
        while True:
            message = await receive(reader)
            kind = message["type"]
            if kind == "arm":
                reason = refusal_reason(
                    store.authorization(),
                    coordinator=fingerprint,
                    target_url=str(message["target_url"]),
                    duration_minutes=float(message["duration_minutes"]),
                    peak_requests_per_minute=float(message["peak_rpm"]),
                    peak_connections=int(message["peak_connections"]),
                )
                if reason is not None:
                    log(f"campaign refused: {reason}")
                    await send(
                        writer,
                        {"type": "refused", "campaign": message["campaign"], "reason": reason},
                    )
                    continue
                authorization = store.authorization()
                assert authorization is not None
                limits = {
                    "rps": authorization.max_requests_per_minute / 60.0,
                    "connections": authorization.max_connections,
                }
                count = max(1, int(message.get("processes", 1)))
                pool = EmitterPool(
                    multiprocessing.get_context("spawn"),
                    count,
                    str(message["target_url"]),
                    _TIMEOUT_SECONDS,
                    OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
                )
                await pool.start()
                log(f"armed: {message['target_url']} ({count} process(es))")
                await send(writer, {"type": "armed", "campaign": message["campaign"]})
            elif kind == "tick" and pool is not None:
                index = int(message["index"])
                rate = min(float(message["rps"]), limits["rps"])  # garde locale, a chaque seconde
                held = min(int(message["connections"]), limits["connections"])
                pool.tick(index, split_rate(rate, pool.size), split_count(held, pool.size))
                reports = await pool.reports(index)
                await send(
                    writer, {"type": "report", "index": index, "data": merge_reports(reports)}
                )
            elif kind == "end":
                if pool is not None:
                    await pool.stop()
                    pool = None
                await send(writer, {"type": "done"})
                log("campaign finished")
                if once:
                    return 0
    except (ProtocolError, ConnectionError, OSError) as error:
        log(f"connection lost: {error}")
        return 0
    finally:
        if pool is not None:
            await pool.stop()
        writer.close()


def merge_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Comptes de tous les processus du worker, en un seul compte rendu
    (histogrammes additionnes)."""
    from omega_stress.domain.load.histogram import merge

    errors: dict[str, int] = {}
    for report in reports:
        for key, value in report["errors"].items():
            errors[key] = errors.get(key, 0) + value
    return {
        "completed": sum(r["completed"] for r in reports),
        "emitted": sum(r["emitted"] for r in reports),
        "not_emitted": sum(r["not_emitted"] for r in reports),
        "late": sum(r["late"] for r in reports),
        "active": sum(r["active"] for r in reports),
        "errors": errors,
        "histogram": [
            list(pair) for pair in merge(tuple(map(tuple, r["histogram"])) for r in reports)
        ],
    }
