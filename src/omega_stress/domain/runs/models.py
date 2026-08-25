# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites du sous-domaine runs : evenement, resultat agrege, run historise."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily


@dataclass(frozen=True, slots=True)
class RunEvent:
    """Evenement significatif survenu pendant un run (erreur, seuil
    atteint, arret automatique) — voir plan produit, "table evenements"."""

    occurred_at: datetime
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class IntervalSample:
    """Mesure agregee sur un intervalle d'echantillonnage (1s par defaut,
    domain/load/policies.py::SAMPLE_INTERVAL_SECONDS), publiee en continu
    pendant l'execution d'un run."""

    at_second: float
    observed_rate_per_minute: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_count: int
    request_count: int


@dataclass(frozen=True, slots=True)
class LoadResult:
    """Resultat agrege d'un run termine (voir plan produit, "Export
    detaille" et "box metriques")."""

    verdict: RunVerdict
    requested_rate_per_minute: int | None
    observed_rate_per_minute: float | None
    p50_latency_ms: float | None
    p95_latency_ms: float | None
    p99_latency_ms: float | None
    error_count: int
    total_requests: int
    events: tuple[RunEvent, ...] = ()
    samples: tuple[IntervalSample, ...] = ()


@dataclass(frozen=True, slots=True)
class LoadRun:
    """Un run : execution concrete d'un LoadPlan sur une cible, historise
    (voir plan produit, "Historique et exports")."""

    id: str
    profile_id: str | None
    target_id: str
    family: TestFamily
    level: IntensityLevel
    started_at: datetime
    finished_at: datetime | None = None
    result: LoadResult | None = None
    notes: str = ""
    is_precheck: bool = False

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - RunEvent : un evenement horodate survenu pendant un run.
# - IntervalSample : une mesure d'intervalle publiee en continu pendant
#   l'execution (avant agregation finale en LoadResult).
# - LoadResult : agregat final (verdict, metriques, evenements).
# - LoadRun : l'execution elle-meme, avec son etat (en cours si
#   finished_at est None, termine sinon).
# Pourquoi dans domain/runs/ (charte) :
# - Entites metier pures ; aucune de ces classes ne sait comment elle est
#   persistee (SQLite) ni comment elle est executee (runner httpx/asyncio).
# Ce qu'il ne contient PAS :
# - Aucune logique d'execution (c'est application/pipeline/executor.py).
# - Aucune logique de transition d'etat (voir domain/runs/service.py).
# - Aucune construction de rapport formate (voir domain/reports/, phase
#   suivante).
# Points cles :
# - profile_id est optionnel : un run peut etre lance en mode manuel borne
#   (sans profil fige), voir plan produit "Profil : selection d'un profil
#   fige ou mode manuel borne".
# - is_precheck distingue un run de Pre-check (application/commands/
#   run_precheck.py) d'un run des trois familles principales — un
#   Pre-check reste un LoadRun comme un autre (meme historique, meme
#   LoadResult), seul ce booleen permet de le filtrer/reconnaitre.
# - finished_at/result restent None tant que le run est en cours ; leur
#   presence conjointe est un invariant verifie par
#   domain/runs/service.py::finish(), pas ici (une dataclass ne peut pas
#   facilement imposer "les deux ou aucun" sans alourdir __post_init__
#   pour un cas que finish() garantit deja par construction).
# - LoadResult.samples (2026-08-24) : desormais persiste avec le run
#   (infrastructure/storage/sqlite/run_repository.py, colonne JSON dediee)
#   pour permettre un historique complet par intervalle a l'export
#   (JSON "donnees brutes", chronologie HTML) — avant cela, IntervalSample
#   n'existait qu'en flux ephemere pendant l'execution (republie via
#   run_progress_notifier), jamais conserve au-dela du calcul de
#   l'agregat par domain/runs/service.py::aggregate_samples(). Les
#   echantillons individuels restent NEANMOINS toujours produits en flux
#   par ports/load_runner.py de la meme facon qu'avant ; samples se
#   contente d'en garder une copie complete sur le LoadResult final,
#   c'est tout ce qui a change.
# Comment il sera utilise (apercu) :
# - domain/runs/service.py::finish() cloture un LoadRun avec un
#   LoadResult.
# - ports/load_runner.py produit un flux d'IntervalSample.
# - domain/reports/builders.py consomme LoadRun/LoadResult pour construire
#   le contenu logique d'un export.
#---------------------------------------------------------------------->
