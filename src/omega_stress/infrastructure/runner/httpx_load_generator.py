# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Generateur de charge natif httpx/asyncio. Seul point du projet ou `httpx` est importe."""
from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.policies import SAMPLE_INTERVAL_SECONDS
from omega_stress.domain.load.presets import FIXED_RATE_PRESETS
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.infrastructure.runner.async_worker import RequestOutcome, perform_request
from omega_stress.infrastructure.runner.engine_params import (
    IntervalTarget,
    target_for_interval,
    total_intervals,
)
from omega_stress.infrastructure.runner.result_parser import parse_interval

SleepFn = Callable[[float], Awaitable[object]]

USER_AGENT = "omega-stress-httpx/1.0 (test de charge autorise)"
"""Identifie le trafic genere dans les journaux de la cible plutot que de
laisser l'en-tete par defaut de httpx (python-httpx/x.y.z) : un
administrateur qui inspecte ses logs voit un libelle explicite plutot
qu'une signature de bibliotheque generique."""

_MAX_CONCURRENT_CONNECTIONS = max(
    preset.concurrent_connections for preset in FIXED_RATE_PRESETS.values()
)
"""Bug reel rapporte (2026-08-25) : httpx.AsyncClient() sans `limits=`
explicite retombe sur ses valeurs par defaut (max_connections=100,
httpx._config.DEFAULT_LIMITS) — un Test connexions Maximum vise 200
connexions simultanees (domain/load/presets.py::FIXED_RATE_PRESETS) mais
seule la MOITIE partait reellement en parallele, le reste attendant en
silence un slot libre dans le pool, sans qu'aucun message ni metrique ne
le signale (l'utilisateur voyait un run "plus doux" que ce que l'ecran
annoncait, sans explication). Calcule depuis FIXED_RATE_PRESETS (seule
source de verite, jamais une valeur en dur ici, voir domain/load/
policies.py "aucune valeur de seuil/duree/intensite en dehors de ce
fichier") plutot que fige a 200 : suit automatiquement toute revision
future des presets sans modification de ce fichier."""


class HttpxLoadGenerator:
    """Implemente ports/load_runner.py::LoadRunner. Le runner s'execute
    comme tache asynchrone in-process (ARCHITECTURE.md §5, decision de
    cadrage V1), sans processus separe."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._transport = transport
        self._sleep = sleep

    async def run(self, plan: LoadPlan, *, target_url: str) -> AsyncIterator[IntervalSample]:
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            transport=self._transport,
            headers={"User-Agent": USER_AGENT},
            limits=httpx.Limits(
                max_connections=_MAX_CONCURRENT_CONNECTIONS,
                max_keepalive_connections=_MAX_CONCURRENT_CONNECTIONS,
            ),
        ) as client:
            await self._check_reachable(client, target_url)

            for interval_index in range(total_intervals(plan)):
                target = target_for_interval(plan, interval_index)
                outcomes = await self._run_interval(client, target_url, target)
                yield parse_interval(interval_index * SAMPLE_INTERVAL_SECONDS, outcomes)

    async def _check_reachable(self, client: httpx.AsyncClient, target_url: str) -> None:
        """Verifie que la cible repond AVANT de commencer le run. Une
        erreur ici signifie que le run ne peut produire aucune mesure
        exploitable des le depart — distinct d'une erreur ponctuelle en
        cours de run (absorbee par async_worker.py::perform_request dans
        le taux d'erreur normal de l'intervalle)."""
        try:
            await client.get(target_url)
        except httpx.HTTPError as exc:
            raise RunnerFailureError(
                f"Cible {target_url!r} injoignable des le depart : {exc}"
            ) from exc

    async def _run_interval(
        self, client: httpx.AsyncClient, target_url: str, target: IntervalTarget
    ) -> list[RequestOutcome]:
        request_count = (
            round(target.requests_per_second * SAMPLE_INTERVAL_SECONDS)
            if target.requests_per_second > 0
            else target.concurrency
        )

        started = time.perf_counter()
        outcomes: list[RequestOutcome] = []
        if request_count > 0:
            tasks = [perform_request(client, target_url) for _ in range(request_count)]
            outcomes = list(await asyncio.gather(*tasks))

        elapsed = time.perf_counter() - started
        remaining = SAMPLE_INTERVAL_SECONDS - elapsed
        if remaining > 0:
            await self._sleep(remaining)

        return outcomes

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de generation de charge reelle : orchestre
#   engine_params.py (cible par intervalle), async_worker.py (requetes
#   individuelles) et result_parser.py (agregation), au rythme
#   SAMPLE_INTERVAL_SECONDS.
# Pourquoi dans infrastructure/runner/ (charte) :
# - Seul fichier du projet ou `httpx` est importe (verifie par le contrat
#   import-linter "httpx seulement dans infrastructure.runner", voir
#   pyproject.toml).
# Ce qu'il ne contient PAS :
# - Aucune valeur de charge en dur (deleguee a engine_params.py).
# - Aucune decision d'arret sur seuil : ce generateur produit un flux de
#   mesures, c'est application/pipeline/guards/threshold_guard.py (cote
#   consommateur du flux) qui decide d'arreter la consommation — ce
#   fichier ne s'arrete jamais de lui-meme avant la fin du plan.
# Points cles :
# - _check_reachable() est le SEUL endroit ou une RunnerFailureError peut
#   etre levee : une cible injoignable des le premier appel signale que
#   le run ne peut rien produire d'exploitable, distinct d'erreurs
#   ponctuelles en cours de run (comptees normalement dans le taux
#   d'erreur de chaque IntervalSample, jamais une exception).
# - `sleep` est injectable (par defaut asyncio.sleep) : les tests
#   passent une fonction no-op pour executer un plan de plusieurs
#   minutes quasi instantanement, sans attendre le temps reel — seule la
#   logique est exercee, pas le minutage reel.
# - `transport` est injectable (httpx.MockTransport dans les tests) :
#   aucun appel reseau reel n'est necessaire pour tester ce fichier.
# - USER_AGENT (2026-08-24) : applique une seule fois, au niveau du
#   AsyncClient (pas par requete individuelle) — httpx propage cet en-tete
#   par defaut a chaque appel du client, y compris ceux de
#   async_worker.py::perform_request(), sans qu'il ait besoin de le
#   connaitre lui-meme.
# - _run_interval() vise un rythme d'environ SAMPLE_INTERVAL_SECONDS par
#   intervalle (sleep du temps restant apres les requetes), pour que la
#   cadence de publication vers run_progress_notifier reste reguliere
#   meme si la cible repond tres vite.
# - limits=httpx.Limits(...) (2026-08-25, bug reel rapporte : "je suis a
#   0 erreurs [...] quand je fais le meme test avec loader io j'ai pas
#   du tout les memes resultats") : sans ce parametre, httpx.AsyncClient
#   utilise son pool par defaut (max_connections=100) quel que soit le
#   nombre de requetes lancees en parallele par _run_interval() — un Test
#   connexions Maximum (200 cibles, voir domain/load/presets.py) n'en
#   envoyait donc reellement que 100 a la fois, le reste attendant en
#   silence un slot libre. _MAX_CONCURRENT_CONNECTIONS (calcule depuis
#   FIXED_RATE_PRESETS, jamais fige en dur ici) couvre le plus haut
#   besoin des 4 niveaux pour les 3 familles de test.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py injecte une instance dans
#   application/pipeline/executor.py via le port load_runner.
#---------------------------------------------------------------------->
