# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Paliers de calibrage sur le MOTEUR DES RUNS (boucle ouverte multiprocessus, 2026-11-21).

Avant, le calibrage mesurait avec son propre generateur (rafale par seconde, dans la boucle de
l'interface) : il mesurait donc autre chose que ce qu'utilisent les runs. Il emet maintenant avec
les memes processus d'emission (infrastructure/runner/open_loop/), gardes ouverts d'un palier a
l'autre (keep-alive, comme avant), contre le serveur de boucle locale.

Le debit atteint est celui des requetes EMISES A L'HEURE par seconde reelle (ni retenues par le
plafond en vol, ni parties en retard) : c'est la capacite de CETTE machine a emettre. Le serveur de
boucle locale (Python simple) s'effondre bien avant le moteur sous des milliers de connexions
(mesure du 2026-11-21 : 30 req/s terminees pour 1 000 demandees) ; compter les requetes terminees
mesurerait ce serveur, pas la machine. Le taux d'erreur reste calcule sur les reponses recues.
Le parametre VU d'un palier n'est plus un plafond de concurrence : en boucle ouverte, le nombre de
requetes en vol decoule du debit et du temps de reponse."""

from __future__ import annotations

import asyncio
import multiprocessing
import time
from types import TracebackType

from omega_stress.domain.calibration.models import CalibrationStage, StageMeasurement
from omega_stress.domain.calibration.policies import CALIBRATION_STAGES, CALIBRATION_TARGET_PATH
from omega_stress.domain.load.policies import (
    OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
    SAMPLE_INTERVAL_SECONDS,
)
from omega_stress.domain.runs.models import SystemSnapshot
from omega_stress.infrastructure.probe.live_probe import LiveSystemSampler
from omega_stress.infrastructure.runner.engine_params import IntervalTarget
from omega_stress.infrastructure.runner.open_loop.generator import (
    EmitterPool,
    process_count,
    split_count,
    split_rate,
)
from omega_stress.ports.calibration_stage_progress_notifier import (
    CalibrationStageProgressNotifier,
)
from omega_stress.ports.system_sampler import SystemSampler

_TIMEOUT_SECONDS = 10.0


class OpenLoopCalibrationStageRunner:
    """Implemente ports/calibration_stage_runner.py::CalibrationStageRunner."""

    def __init__(self, *, system_sampler: SystemSampler | None = None) -> None:
        self._system_sampler = (
            system_sampler if system_sampler is not None else LiveSystemSampler()
        )
        self._pool: EmitterPool | None = None
        self._pool_url = ""
        self._count = process_count(
            [IntervalTarget(float(stage.rps_target), 0) for stage in CALIBRATION_STAGES]
        )

    async def __aenter__(self) -> OpenLoopCalibrationStageRunner:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._pool is not None:
            await self._pool.stop()
            self._pool = None

    async def _ensure_pool(self, url: str) -> EmitterPool:
        if self._pool is None or self._pool_url != url:
            if self._pool is not None:
                await self._pool.stop()
            pool = EmitterPool(
                multiprocessing.get_context("spawn"),
                self._count,
                url,
                _TIMEOUT_SECONDS,
                OPEN_LOOP_INFLIGHT_CAP_PER_PROCESS,
            )
            await pool.start()
            self._pool, self._pool_url = pool, url
        return self._pool

    async def run_stage(
        self,
        stage: CalibrationStage,
        *,
        base_url: str,
        stage_progress_notifier: CalibrationStageProgressNotifier,
    ) -> StageMeasurement:
        """Emet stage.rps_target requetes par seconde pendant stage.window_seconds. idle_baseline
        (rps 0) n'emet rien et echantillonne seulement le bruit de fond systeme."""
        url = f"{base_url}{CALIBRATION_TARGET_PATH}"
        pool = await self._ensure_pool(url) if stage.rps_target > 0 else None
        loop = asyncio.get_running_loop()
        started = loop.time()
        previous_end = time.monotonic()
        system_samples: list[SystemSnapshot] = []
        total_completed = total_errors = total_on_time = 0
        max_streak = streak = 0
        real_duration = 0.0
        for second in range(stage.window_seconds):
            delay = started + second * SAMPLE_INTERVAL_SECONDS - loop.time()
            if delay > 0:
                await asyncio.sleep(delay)
            if pool is not None:
                pool.tick(
                    second,
                    split_rate(float(stage.rps_target), self._count),
                    split_count(0, self._count),
                )
                reports = await pool.reports(second)
                completed = sum(r["completed"] for r in reports)
                errors = sum(sum(r["errors"].values()) for r in reports)
                timeouts = sum(r["errors"]["timeout"] for r in reports)
                total_completed += completed
                total_on_time += sum(r["emitted"] - r["late"] for r in reports)
                total_errors += errors
                # Delais depasses enchaines : une seconde sans reponse reussie prolonge la serie.
                if timeouts and completed - errors <= 0:
                    streak += timeouts
                    max_streak = max(max_streak, streak)
                elif completed - errors > 0:
                    streak = 0
            else:
                await asyncio.sleep(SAMPLE_INTERVAL_SECONDS)
            now = time.monotonic()
            real_duration += max(SAMPLE_INTERVAL_SECONDS, now - previous_end)
            previous_end = now
            system_samples.append(self._system_sampler.sample())
            stage_progress_notifier.notify(stage.id, second + 1, stage.window_seconds)
        return StageMeasurement(
            rps_achieved=total_on_time / real_duration if real_duration > 0 else 0.0,
            error_rate=total_errors / total_completed if total_completed > 0 else 0.0,
            system_samples=tuple(system_samples),
            consecutive_timeouts=max_streak,
        )
