# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Execution d'UN palier de calibrage contre le serveur de boucle locale
(local_server.py). Seul point du sous-domaine calibration ou `httpx` est
importe — reutilise les primitives de plus bas niveau deja ecrites et
testees pour les runs reels (async_worker.py, live_probe.py) plutot que
de dupliquer une seconde boucle de generation de charge."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from types import TracebackType

import httpx

from omega_stress.domain.calibration.models import CalibrationStage, StageMeasurement
from omega_stress.domain.calibration.policies import CALIBRATION_STAGES, CALIBRATION_TARGET_PATH
from omega_stress.domain.load.policies import SAMPLE_INTERVAL_SECONDS
from omega_stress.domain.runs.models import SystemSnapshot
from omega_stress.infrastructure.probe.live_probe import LiveSystemSampler
from omega_stress.infrastructure.runner.async_worker import perform_request
from omega_stress.ports.calibration_stage_progress_notifier import (
    CalibrationStageProgressNotifier,
)
from omega_stress.ports.system_sampler import SystemSampler

SleepFn = Callable[[float], Awaitable[object]]

_MAX_STAGE_VU = max(stage.vu_target for stage in CALIBRATION_STAGES)
"""Meme bug reel a eviter que infrastructure/runner/httpx_load_generator.py
::_MAX_CONCURRENT_CONNECTIONS (2026-08-25) : httpx.AsyncClient() sans
`limits=` explicite retombe sur son pool par defaut (max_connections=100),
qui plafonnerait silencieusement les paliers a VU eleve (calib_5=1000,
calib_6=2000) bien avant tout seuil de sante/arret reel — calcule depuis
CALIBRATION_STAGES (seule source de verite), jamais fige en dur ici."""


class HttpxCalibrationStageRunner:
    """Gestionnaire de contexte asynchrone : garde un seul httpx.AsyncClient
    ouvert (keep-alive, document : "Keep-alive : active") sur toute la
    progression de paliers, plutot que d'en reconstruire un par palier."""

    def __init__(
        self,
        *,
        system_sampler: SystemSampler | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        # Construit ICI si non fourni (jamais comme valeur par defaut du
        # parametre) : meme raison que HttpxLoadGenerator, chaque instance
        # garde son propre etat psutil.Process().
        self._system_sampler = system_sampler if system_sampler is not None else LiveSystemSampler()
        self._sleep = sleep
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> HttpxCalibrationStageRunner:
        self._client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(
                max_connections=_MAX_STAGE_VU, max_keepalive_connections=_MAX_STAGE_VU
            ),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def run_stage(
        self,
        stage: CalibrationStage,
        *,
        base_url: str,
        stage_progress_notifier: CalibrationStageProgressNotifier,
    ) -> StageMeasurement:
        """Emet stage.rps_target requetes par seconde reelle, pendant
        stage.window_seconds, bornees a stage.vu_target requetes EN VOL
        simultanement (semaphore) — VU = concurrence maximale, RPS =
        debit cible, les deux dimensions du document appliquees ensemble
        plutot que la famille exclusive (Requetes OU Connexions) des runs
        reels. idle_baseline (vu=0, rps=0) n'emet aucune requete, se
        contente d'echantillonner le bruit de fond systeme."""
        if self._client is None:
            raise RuntimeError(
                "HttpxCalibrationStageRunner.run_stage() appelee hors du "
                "gestionnaire de contexte (async with)."
            )
        client = self._client
        url = f"{base_url}{CALIBRATION_TARGET_PATH}"
        semaphore = asyncio.Semaphore(max(stage.vu_target, 1))

        system_samples: list[SystemSnapshot] = []
        total_requests = 0
        total_errors = 0
        max_consecutive_timeouts = 0
        current_timeout_streak = 0

        for _second in range(stage.window_seconds):
            started = time.perf_counter()
            if stage.rps_target > 0:

                async def _one() -> str | None:
                    async with semaphore:
                        outcome = await perform_request(client, url)
                        return outcome.error_category if not outcome.success else None

                error_categories = list(
                    await asyncio.gather(*(_one() for _ in range(stage.rps_target)))
                )
                total_requests += len(error_categories)
                for category in error_categories:
                    if category is not None:
                        total_errors += 1
                    if category == "timeout":
                        current_timeout_streak += 1
                        max_consecutive_timeouts = max(
                            max_consecutive_timeouts, current_timeout_streak
                        )
                    else:
                        current_timeout_streak = 0

            elapsed = time.perf_counter() - started
            remaining = SAMPLE_INTERVAL_SECONDS - elapsed
            if remaining > 0:
                await self._sleep(remaining)
            system_samples.append(self._system_sampler.sample())
            stage_progress_notifier.notify(stage.id, _second + 1, stage.window_seconds)

        error_rate = total_errors / total_requests if total_requests > 0 else 0.0
        rps_achieved = (
            total_requests / stage.window_seconds if stage.window_seconds > 0 else 0.0
        )
        return StageMeasurement(
            rps_achieved=rps_achieved,
            error_rate=error_rate,
            system_samples=tuple(system_samples),
            consecutive_timeouts=max_consecutive_timeouts,
        )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Emet la charge d'UN palier de calibrage contre le serveur de boucle
#   locale et agrege une StageMeasurement brute (aucun jugement sante/
#   arret ici, voir domain/calibration/validators.py::
#   evaluate_stage_outcome()).
# Pourquoi dans infrastructure/calibration/ (charte) :
# - Seul point du sous-domaine calibration ou httpx est importe — le
#   contrat import-linter "httpx seulement dans infrastructure.runner"
#   n'exclut PAS infrastructure/ elle-meme de ses source_modules (deja
#   le cas pour les 3 autres contrats a bibliotheque unique du projet,
#   voir pyproject.toml) : un sous-module infrastructure SIBLING peut
#   importer httpx, meme precedent que ce fichier applique ici plutot
#   que de dupliquer HttpxLoadGenerator ou de le detourner de son usage
#   (LoadPlan/Duration en MINUTES, incompatible avec des fenetres de
#   5-20 SECONDES, voir plus bas).
# Ce qu'il ne contient PAS :
# - Aucune construction de LoadPlan/Duration : domain/load/models.py::
#   Duration est en minutes ENTIERES (Duration.minutes: int), incompatible
#   avec les fenetres de palier (5/10/15/20 secondes) — plutot que de
#   forcer cette abstraction (concue pour le systeme de niveaux/profils
#   utilisateur) a porter un cas qu'elle ne represente pas, ce fichier
#   reutilise les primitives de PLUS BAS niveau directement
#   (async_worker.py::perform_request(), live_probe.py::LiveSystemSampler)
#   dans sa propre boucle, dediee aux couples VU/RPS arbitraires des
#   paliers.
# - Aucune decision sante/arret (voir domain/calibration/validators.py) :
#   ce fichier mesure, ne juge jamais.
# Points cles :
# - stage_progress_notifier.notify() (2026-09-02, bug reel rapporte :
#   "le calibrage semble geler" sur un palier plus lent que prevu, voir
#   ports/calibration_stage_progress_notifier.py pour le diagnostic
#   complet) : appelee a CHAQUE tour de la boucle par seconde, apres
#   l'echantillonnage systeme — jamais avant (l'ecran affiche ainsi une
#   seconde REELLEMENT ecoulee, pas une seconde sur le point de commencer).
# - `sleep`/`system_sampler` injectables (meme patron que
#   HttpxLoadGenerator) : les tests passent un sleep no-op pour executer
#   un palier de 20s quasi instantanement.
# - Boucle par seconde calquee sur infrastructure/runner/
#   httpx_load_generator.py::_run_interval() (meme rythme cible via
#   time.perf_counter() + sleep du temps restant) : deux implementations
#   separees (Duration en minutes vs fenetre en secondes empechent une
#   fonction commune), mais le MEME PRINCIPE de cadence.
# - consecutive_timeouts : approxime sur l'ordre de retour de
#   asyncio.gather() (qui correspond a l'ordre des coroutines soumises,
#   pas necessairement l'ordre de completion reel) — approximation
#   assumee, suffisante pour un signal heuristique de securite, jamais
#   une mesure de concurrence rigoureuse.
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py : `async with
#   HttpxCalibrationStageRunner() as runner:` autour de toute la
#   progression, un appel a run_stage() par palier.
#---------------------------------------------------------------------->
