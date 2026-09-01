# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites du sous-domaine runs : evenement, resultat agrege, run historise."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from omega_stress.core.enums import DurationPresetId, IntensityLevel, RunVerdict, TestFamily


@dataclass(frozen=True, slots=True)
class RunEvent:
    """Evenement significatif survenu pendant un run (erreur, seuil
    atteint, arret automatique) — voir plan produit, "table evenements"."""

    occurred_at: datetime
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class ErrorBreakdown:
    """Repartition des echecs d'un intervalle (ou d'un run entier) par
    categorie — Phase 1 observabilite (omega-stress-calibrage-profils-
    securite.md). `timeout`/`connection` distinguent un echec reseau
    d'un statut HTTP effectivement recu (4xx/5xx) : necessaire pour
    distinguer plus tard une cible qui repond mal (HTTP) d'un reseau ou
    d'un generateur limitant (Phases 2/5), jamais melanges dans un seul
    compteur d'erreur."""

    timeout: int = 0
    connection: int = 0
    http_4xx: int = 0
    http_5xx: int = 0
    other: int = 0

    @property
    def total(self) -> int:
        return self.timeout + self.connection + self.http_4xx + self.http_5xx + self.other


@dataclass(frozen=True, slots=True)
class SystemSnapshot:
    """Photo des ressources systeme locales prise pendant un intervalle
    d'echantillonnage (Phase 1 observabilite) — distinct de
    ports/system_probe.py, explicitement pre-flight uniquement. Tout
    champ reste `None` si sa mesure a echoue plutot que de faire
    echouer le run (voir infrastructure/probe/live_probe.py).

    open_files_soft_limit (Phase 2 garde-fous) : limite douce de
    descripteurs de fichiers ouverts du processus, lue une seule fois
    (un ulimit ne change pas en cours de run) et reportee sur chaque
    snapshot — necessaire pour que domain/load/validators.py puisse
    calculer un ratio d'usage en pur domaine, sans appeler
    infrastructure/ (Dependency Rule).

    logical_cpu_count (2026-09-01, correction de bug reel) : nombre de
    coeurs logiques de la machine, lu une seule fois (ne change pas en
    cours de run) — cpu_percent_generator est deja normalise sur cette
    base (0-100, comparable a cpu_percent_global), mais domain/load/
    validators.py::evaluate_generator_resources() a aussi besoin du
    nombre de coeurs pour calculer un seuil d'arret UNIVERSEL (relatif a
    ce qu'un seul coeur peut fournir, voir policies.py::
    GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE) plutot qu'un pourcentage
    absolu fixe, quasiment inatteignable des 4 coeurs et systematiquement
    atteint sur 1-2 coeurs sinon."""

    cpu_percent_generator: float | None = None
    cpu_percent_global: float | None = None
    memory_available_percent: float | None = None
    memory_rss_mb: float | None = None
    swap_used_mb: float | None = None
    open_files: int | None = None
    open_files_soft_limit: int | None = None
    logical_cpu_count: int | None = None


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
    requested_rate_per_minute: float | None = None
    active_connections: int = 0
    errors: ErrorBreakdown = field(default_factory=ErrorBreakdown)
    system: SystemSnapshot | None = None


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
    errors: ErrorBreakdown = field(default_factory=ErrorBreakdown)
    peak_cpu_percent_generator: float | None = None
    peak_memory_rss_mb: float | None = None


@dataclass(frozen=True, slots=True)
class LoadRun:
    """Un run : execution concrete d'un LoadPlan sur une cible, historise
    (voir plan produit, "Historique et exports").

    duration_preset_id : copie de LoadPlan.duration_preset_id (domain/
    load/models.py) au moment du lancement — None si le run a ete lance
    en mode manuel. Portee ici (pas seulement sur LoadPlan, ephemere) pour
    que l'historique/export sache quel profil D1-D6 a ete utilise apres
    coup (voir domain/load/duration_presets.py).

    safety_mode : copie de LoadPlan.safety_mode (2026-09-01, "mode
    securite" a cocher) au moment du lancement — meme raison exacte que
    duration_preset_id, pour qu'un rapport puisse dire honnetement si les
    garde-fous locaux (CPU/memoire/FDs) etaient actifs pendant ce run."""

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
    duration_preset_id: DurationPresetId | None = None
    safety_mode: bool = True

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - RunEvent : un evenement horodate survenu pendant un run.
# - ErrorBreakdown : repartition des echecs par categorie (Phase 1).
# - SystemSnapshot : photo CPU/RAM/swap/FDs du generateur (Phase 1),
#   distincte de ports/system_probe.py (pre-flight uniquement).
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
