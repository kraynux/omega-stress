# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat du serveur de boucle locale, cible du calibrage."""
from __future__ import annotations

from types import TracebackType
from typing import Protocol


class CalibrationServer(Protocol):
    """Implemente par infrastructure/calibration/local_server.py::
    CalibrationLocalServer — gestionnaire de contexte SYNCHRONE (le
    serveur tourne dans un thread OS separe, jamais sur la boucle
    asyncio, voir son propre INFO DEV)."""

    def __enter__(self) -> CalibrationServer: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    @property
    def base_url(self) -> str:
        """URL de base (`http://127.0.0.1:<port ephemere>`), disponible
        seulement APRES l'entree dans le contexte."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat du serveur local servant de cible au calibrage.
# Pourquoi dans ports/ (charte) :
# - application/commands/run_calibration.py ne peut jamais importer
#   infrastructure/calibration/local_server.py directement (Dependency
#   Rule) — recoit une FACTORY (Callable[[], CalibrationServer]) injectee
#   par app/dependency_container.py, jamais la classe concrete.
# Ce qu'il ne contient PAS :
# - Aucune logique HTTP (voir infrastructure/calibration/local_server.py).
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py : `with server_factory() as
#   server:` autour de toute la progression de paliers.
#---------------------------------------------------------------------->
