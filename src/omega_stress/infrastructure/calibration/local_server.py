# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Serveur de boucle locale integre a Omega-Stress, cible du calibrage
(voir domain/calibration/policies.py::CALIBRATION_TARGET_PATH/
CALIBRATION_PAYLOAD_SIZE_BYTES et document produit, "Cible de
calibrage") — evite de melanger les performances du generateur avec
Internet, Wi-Fi, CDN, DNS, WAF, proxy, latence distante ou capacite d'un
serveur tiers."""
from __future__ import annotations

import http.server
import threading
from types import TracebackType

from omega_stress.domain.calibration.policies import (
    CALIBRATION_PAYLOAD_SIZE_BYTES,
    CALIBRATION_TARGET_PATH,
)

_PAYLOAD = b"o" * CALIBRATION_PAYLOAD_SIZE_BYTES


class _CalibrationRequestHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # active le keep-alive (document : "Keep-alive : active")

    def do_GET(self) -> None:
        if self.path != CALIBRATION_TARGET_PATH:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(CALIBRATION_PAYLOAD_SIZE_BYTES))
        self.end_headers()
        self.wfile.write(_PAYLOAD)

    def log_message(self, format: str, *args: object) -> None:
        """No-op : document, "Logs par requete : desactives" — un
        calibrage peut emettre des milliers de requetes, journaliser
        chacune sur stderr (comportement par defaut de BaseHTTPRequestHandler)
        noierait toute autre sortie de l'application."""


class CalibrationLocalServer:
    """Gestionnaire de contexte : demarre/arrete le serveur de boucle
    locale. Port EPHEMERE (bind sur 0, choisi par l'OS) — simplifie la
    precondition "port local de calibrage indisponible" du document
    produit (rien a verifier explicitement, l'OS garantit un port libre
    au moment du bind)."""

    def __init__(self) -> None:
        self._httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _CalibrationRequestHandler)
        self._thread: threading.Thread | None = None

    def __enter__(self) -> CalibrationLocalServer:
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5.0)

    @property
    def base_url(self) -> str:
        port = self._httpd.server_address[1]
        return f"http://127.0.0.1:{port}"

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
