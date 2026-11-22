# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Client HTTP/1.1 minimal sur une connexion TCP/TLS TENUE (Test connexions, lecture B, 2026-11-21).

Une connexion = une socket ouverte et gardee (keep-alive) ; elle envoie un GET a chaque echeance et
lit la reponse en entier (Content-Length, chunked, ou jusqu'a la fermeture). httpx partage ses
connexions dans un pool : il n'ouvre que celles dont le debit a besoin, alors que ce test doit en
TENIR N."""

from __future__ import annotations

import asyncio
import contextlib
import ssl
from dataclasses import dataclass
from urllib.parse import urlsplit

MAX_HEADER_BYTES = 64 * 1024


@dataclass(frozen=True, slots=True)
class Target:
    host: str
    port: int
    tls: bool
    request: bytes


def parse_target(url: str, user_agent: str) -> Target:
    parts = urlsplit(url)
    tls = parts.scheme == "https"
    host = parts.hostname or "localhost"
    port = parts.port or (443 if tls else 80)
    path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    authority = host if parts.port is None else f"{host}:{parts.port}"
    request = (
        f"GET {path} HTTP/1.1\r\nHost: {authority}\r\nUser-Agent: {user_agent}\r\n"
        "Accept: */*\r\nConnection: keep-alive\r\n\r\n"
    ).encode("ascii", "ignore")
    return Target(host, port, tls, request)


class _StaleConnection(Exception):
    """Connexion fermee par la cible avant tout octet de reponse."""


class HeldConnection:
    """Une connexion gardee ouverte ; `get()` rend le code HTTP, ou leve
    OSError/asyncio.TimeoutError."""

    def __init__(self, target: Target, ssl_context: ssl.SSLContext | None) -> None:
        self._target = target
        self._ssl = ssl_context if target.tls else None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    @property
    def is_open(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def open(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(
            self._target.host,
            self._target.port,
            ssl=self._ssl,
            server_hostname=self._target.host if self._ssl else None,
        )

    async def get(self) -> int:
        """Une requete. Une connexion REUTILISEE que la cible a fermee entre-temps (delai
        d'inactivite : 5 s chez Apache, 75 s chez nginx ; HTTP/1.0 : apres chaque reponse) est
        rouverte et la requete renvoyee une fois, si rien n'a ete recu (correctif 2.0.0,
        2026-11-21 : ces fermetures normales comptaient comme des erreurs de connexion)."""
        reused = self.is_open
        if not reused:
            await self.open()
        try:
            return await self._exchange()
        except _StaleConnection:
            await self.close()
            if not reused:
                raise OSError("connection closed by the target before any response") from None
            await self.open()
            try:
                return await self._exchange()
            except _StaleConnection:
                await self.close()
                raise OSError("connection closed by the target before any response") from None

    async def _exchange(self) -> int:
        assert self._reader is not None and self._writer is not None
        try:
            self._writer.write(self._target.request)
            await self._writer.drain()
            head = await self._reader.readuntil(b"\r\n\r\n")
        except asyncio.IncompleteReadError as error:
            if error.partial:
                raise
            raise _StaleConnection from None
        except (ConnectionResetError, BrokenPipeError):
            raise _StaleConnection from None
        if len(head) > MAX_HEADER_BYTES:
            raise OSError("response headers too large")
        lines = head.decode("latin-1").split("\r\n")
        version, status_text = lines[0].split(" ", 2)[:2]
        status = int(status_text)
        headers = {}
        for line in lines[1:]:
            name, _, value = line.partition(":")
            if name:
                headers[name.strip().lower()] = value.strip().lower()
        if "chunked" in headers.get("transfer-encoding", ""):
            await self._read_chunked()
        elif "content-length" in headers:
            await self._reader.readexactly(int(headers["content-length"]))
        else:
            await self._reader.read()  # jusqu'a la fermeture par la cible
            await self.close()
        connection = headers.get("connection", "")
        if connection == "close" or (version == "HTTP/1.0" and connection != "keep-alive"):
            await self.close()
        return status

    async def _read_chunked(self) -> None:
        assert self._reader is not None
        while True:
            size_line = await self._reader.readuntil(b"\r\n")
            size = int(size_line.split(b";", 1)[0].strip() or b"0", 16)
            if size == 0:
                while (await self._reader.readuntil(b"\r\n")) != b"\r\n":
                    pass
                return
            await self._reader.readexactly(size + 2)

    async def close(self) -> None:
        writer, self._writer, self._reader = self._writer, None, None
        if writer is not None:
            writer.close()
            with contextlib.suppress(OSError, ssl.SSLError):
                await writer.wait_closed()
