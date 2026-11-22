# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Canal de controle coordinateur <-> worker (Phase 2, 2026-11-21) : un objet JSON par ligne, sur
une connexion TLS. Messages (champ "type") :

worker -> coordinateur : pair{code,name} | hello{worker_id,secret,version,capacity_rps,cpus}
                         armed{campaign} | refused{campaign,reason} | report{index,data} | done
coordinateur -> worker : paired{worker_id,secret} | welcome | rejected{reason}
                         arm{campaign,target_url,duration_minutes,peak_rpm,peak_connections,
                             processes} | tick{index,rps,connections} | end"""

from __future__ import annotations

import asyncio
import json
from typing import Any

MAX_LINE_BYTES = 4 * 1024 * 1024


class ProtocolError(RuntimeError):
    pass


async def send(writer: asyncio.StreamWriter, message: dict[str, Any]) -> None:
    writer.write(json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n")
    await writer.drain()


async def receive(reader: asyncio.StreamReader, timeout: float | None = None) -> dict[str, Any]:
    try:
        line = await asyncio.wait_for(reader.readuntil(b"\n"), timeout)
    except asyncio.IncompleteReadError as error:
        raise ProtocolError("connection closed") from error
    except asyncio.LimitOverrunError as error:
        raise ProtocolError("message too large") from error
    try:
        message = json.loads(line)
    except ValueError as error:
        raise ProtocolError("invalid message") from error
    if not isinstance(message, dict) or not isinstance(message.get("type"), str):
        raise ProtocolError("invalid message")
    return message
