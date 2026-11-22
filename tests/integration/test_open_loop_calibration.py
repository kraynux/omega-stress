# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Calibrage sur le moteur des runs (boucle ouverte, 2026-11-21), contre le serveur de boucle
locale."""

from __future__ import annotations

import asyncio

from omega_stress.domain.calibration.models import CalibrationStage
from omega_stress.infrastructure.calibration.local_server import CalibrationLocalServer
from omega_stress.infrastructure.calibration.open_loop_stage_runner import (
    OpenLoopCalibrationStageRunner,
)


class _Progress:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, int]] = []

    def notify(self, stage_id: str, second: int, total: int) -> None:
        self.calls.append((stage_id, second, total))


def test_paliers_mesures_par_le_moteur_des_runs() -> None:
    stages = [
        CalibrationStage(id="idle_baseline", name="repos", vu_target=0, rps_target=0,
                         window_seconds=1, conditional=False),
        CalibrationStage(id="calib_1", name="p1", vu_target=25, rps_target=50,
                         window_seconds=3, conditional=False),
        CalibrationStage(id="calib_2", name="p2", vu_target=100, rps_target=150,
                         window_seconds=3, conditional=False),
    ]
    progress = _Progress()

    async def go() -> list:
        with CalibrationLocalServer() as server:
            async with OpenLoopCalibrationStageRunner() as runner:
                return [await runner.run_stage(stage, base_url=server.base_url,
                                               stage_progress_notifier=progress)
                        for stage in stages]

    idle, first, second = asyncio.run(go())
    assert idle.rps_achieved == 0.0 and len(idle.system_samples) == 1
    assert 40 <= first.rps_achieved <= 55 and first.error_rate == 0.0
    assert 120 <= second.rps_achieved <= 160 and second.error_rate == 0.0
    assert progress.calls[-1] == ("calib_2", 3, 3)
