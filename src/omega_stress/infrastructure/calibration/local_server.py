# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Serveur de boucle locale integre a Omega-Stress, cible du calibrage
(voir domain/calibration/policies.py::CALIBRATION_TARGET_PATH/
CALIBRATION_PAYLOAD_SIZE_BYTES et document produit, "Cible de
calibrage") — evite de melanger les performances du generateur avec
Internet, Wi-Fi, CDN, DNS, WAF, proxy, latence distante ou capacite d'un
serveur tiers."""
from __future__ import annotations

import asyncio
import contextlib
import multiprocessing
import os
import signal
import sys
from types import TracebackType
from typing import Any

from omega_stress.domain.calibration.policies import (
    CALIBRATION_PAYLOAD_SIZE_BYTES,
    CALIBRATION_TARGET_PATH,
)
from omega_stress.infrastructure.process_start import start_process
from omega_stress.shared.i18n import _

_PAYLOAD = b"o" * CALIBRATION_PAYLOAD_SIZE_BYTES
_OK = (
    b"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n"
    + f"Content-Length: {CALIBRATION_PAYLOAD_SIZE_BYTES}\r\n\r\n".encode("ascii")
    + _PAYLOAD
)
_NOT_FOUND = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
_START_TIMEOUT_SECONDS = 30.0


def _serve(conn: Any) -> None:
    """Processus du serveur (2026-11-21) : asyncio, keep-alive, une reponse fixe. Separe de
    l'interface et du pilote du moteur : il ne leur dispute plus le GIL. Les journaux par
    requete restent desactives (document : « Logs par requete : desactives »)."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    sys.stdout = sys.stderr = open(os.devnull, "w")  # noqa: SIM115
    asyncio.run(_main(conn))


async def _main(conn: Any) -> None:
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while True:
                head = await reader.readuntil(b"\r\n\r\n")
                parts = head.split(b"\r\n", 1)[0].split(b" ")
                path = parts[1].decode("latin-1") if len(parts) > 1 else ""
                writer.write(_OK if path == CALIBRATION_TARGET_PATH else _NOT_FOUND)
                await writer.drain()
        except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, ConnectionError):
            pass
        finally:
            writer.close()

    server = await asyncio.start_server(handle, "127.0.0.1", 0, backlog=4096)
    conn.send(server.sockets[0].getsockname()[1])
    loop = asyncio.get_running_loop()
    with contextlib.suppress(EOFError, OSError):
        await loop.run_in_executor(None, conn.recv)  # ordre d'arret, ou fermeture du tuyau
    server.close()


class CalibrationLocalServer:
    """Gestionnaire de contexte : demarre/arrete le serveur de boucle locale, dans son propre
    processus (2026-11-21 ; avant : http.server a un fil par connexion dans le processus de
    l'interface, qui s'effondrait sous la charge du moteur en boucle ouverte et faussait le
    calibrage). Port EPHEMERE (bind sur 0, choisi par l'OS) — simplifie la precondition « port
    local de calibrage indisponible » du document produit."""

    def __init__(self) -> None:
        context = multiprocessing.get_context("spawn")
        self._conn, child = context.Pipe()
        self._process = context.Process(target=_serve, args=(child,), daemon=True)
        self._child = child
        self._port = 0

    def __enter__(self) -> CalibrationLocalServer:
        start_process(self._process)
        self._child.close()
        if not self._conn.poll(_START_TIMEOUT_SECONDS):
            self._process.terminate()
            raise RuntimeError(_("Le serveur de calibrage local n'a pas démarré."))
        self._port = int(self._conn.recv())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        with contextlib.suppress(BrokenPipeError, OSError):
            self._conn.send("stop")
        self._process.join(timeout=5.0)
        if self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=2.0)
        self._conn.close()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self._port}"


# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Serveur HTTP minimal, cible du calibrage : repond a un chemin fixe
#   avec une charge utile fixe et deterministe, rien d'autre.
# Pourquoi dans infrastructure/calibration/ (charte) :
# - Detail d'execution technique concret (un vrai serveur socket),
#   jamais une regle de domaine — CALIBRATION_TARGET_PATH/
#   CALIBRATION_PAYLOAD_SIZE_BYTES restent dans domain/calibration/
#   policies.py, ce fichier ne fait que les servir.
# Ce qu'il ne contient PAS :
# - Aucune nouvelle dependance : http.server/threading/socketserver sont
#   stdlib — coherent avec la philosophie du projet (voir par exemple
#   infrastructure/exporters/time_series_chart.py, SVG dessine a la main
#   plutot qu'une bibliotheque de graphes).
# - Aucune boucle asyncio : ThreadingHTTPServer.serve_forever() est
#   BLOQUANT, execute dans un thread demon separe pour ne jamais
#   bloquer la boucle asyncio de l'application (Textual + le client
#   httpx du calibrage, voir stage_runner.py) — les deux mondes
#   (thread OS classique, boucle asyncio) ne se gene naient jamais ici,
#   seule la socket TCP les relie.
# Points cles :
# - Port ephemere (0) : properiete base_url lit le port REELLEMENT
#   attribue via server_address APRES le bind (deja effectue par
#   ThreadingHTTPServer.__init__, avant meme __enter__()) — jamais un
#   port fixe suppose libre.
# - _CalibrationRequestHandler.log_message() surcharge en no-op : sans
#   cela, chaque requete de calibrage (des milliers potentiellement)
#   ecrirait une ligne sur stderr (comportement par defaut de la classe
#   stdlib), polluant toute sortie CLI/notification de l'application.
# - __exit__() : shutdown() (arrete la boucle serve_forever()) PUIS
#   server_close() (libere la socket) PUIS join() sur le thread avec un
#   timeout de securite — jamais suppose que le thread s'arrete
#   instantanement.
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py : `with CalibrationLocalServer()
#   as server:` autour de toute la progression de paliers.
# - infrastructure/calibration/stage_runner.py requete server.base_url +
#   CALIBRATION_TARGET_PATH.
#---------------------------------------------------------------------->
