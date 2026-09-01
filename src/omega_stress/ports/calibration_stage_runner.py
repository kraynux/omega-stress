# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat d'execution d'UN palier de calibrage contre le serveur local."""
from __future__ import annotations

from types import TracebackType
from typing import Protocol

from omega_stress.domain.calibration.models import CalibrationStage, StageMeasurement
from omega_stress.ports.calibration_stage_progress_notifier import (
    CalibrationStageProgressNotifier,
)


class CalibrationStageRunner(Protocol):
    """Implemente par infrastructure/calibration/stage_runner.py::
    HttpxCalibrationStageRunner — gestionnaire de contexte ASYNCHRONE
    (garde un client HTTP garde-vivant ouvert sur toute la progression
    de paliers)."""

    async def __aenter__(self) -> CalibrationStageRunner: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def run_stage(
        self,
        stage: CalibrationStage,
        *,
        base_url: str,
        stage_progress_notifier: CalibrationStageProgressNotifier,
    ) -> StageMeasurement:
        """Emet la charge d'UN palier et retourne sa mesure brute (aucun
        verdict sante/arret — voir domain/calibration/validators.py::
        evaluate_stage_outcome(), consommateur de cette mesure).
        stage_progress_notifier.notify() est appelee CHAQUE seconde de la
        fenetre (2026-09-02, bug reel rapporte : "le calibrage semble
        geler" sur un palier plus lent que prevu, voir ports/calibration_
        stage_progress_notifier.py pour le diagnostic complet)."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat d'execution d'un palier de calibrage.
# Pourquoi dans ports/ (charte) :
# - Meme raison que ports/calibration_local_server.py : application/
#   commands/run_calibration.py recoit une FACTORY injectee, jamais la
#   classe concrete (qui importe httpx, interdit hors infrastructure/).
# Ce qu'il ne contient PAS :
# - Aucune logique HTTP/asyncio.gather (voir infrastructure/calibration/
#   stage_runner.py).
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py : `async with
#   stage_runner_factory() as runner:` autour de toute la progression,
#   un appel a run_stage() par palier de domain/calibration/policies.py::
#   CALIBRATION_STAGES.
#---------------------------------------------------------------------->
