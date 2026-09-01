# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites du sous-domaine calibration : palier, resultat de palier,
enveloppe sure, empreinte machine, resultat complet persiste."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_stress.domain.runs.models import SystemSnapshot


@dataclass(frozen=True, slots=True)
class CalibrationPreconditionsSnapshot:
    """Mesures brutes necessaires a domain/calibration/validators.py::
    evaluate_preconditions() — produites par infrastructure/calibration/
    preconditions_probe.py, jamais mesurees dans domain/."""

    cpu_global_percent: float | None
    memory_available_percent: float | None
    swap_active_or_growing: bool
    load_average_1min: float | None
    logical_cpu_count: int


@dataclass(frozen=True, slots=True)
class CalibrationStage:
    """Un palier de la progression de calibrage (voir domain/calibration/
    policies.py::CALIBRATION_STAGES) — VU/RPS sont des OBJECTIFS envoyes
    au regulateur, jamais garantis atteints (CalibrationStageResult porte
    la valeur reellement mesuree)."""

    id: str
    name: str
    vu_target: int
    rps_target: int
    window_seconds: int
    conditional: bool


@dataclass(frozen=True, slots=True)
class StageMeasurement:
    """Mesure brute d'UN palier deja execute, avant tout verdict sante/
    arret — produite par infrastructure/calibration/stage_runner.py,
    consommee par domain/calibration/validators.py::
    evaluate_stage_outcome() (qui produit alors un CalibrationStageResult
    complet ci-dessous). Distinct de CalibrationStageResult : ce type ne
    porte aucun jugement (is_healthy/stop_reason), seulement des faits
    mesures."""

    rps_achieved: float
    error_rate: float
    system_samples: tuple[SystemSnapshot, ...]
    consecutive_timeouts: int


@dataclass(frozen=True, slots=True)
class CalibrationStageResult:
    """Mesure et verdict pour UN palier deja execute."""

    stage_id: str
    vu_target: int
    rps_target: int
    rps_achieved: float
    error_rate: float
    peak_cpu_percent_generator: float | None
    peak_cpu_percent_global: float | None
    memory_available_percent_min: float | None
    is_healthy: bool
    stop_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CalibrationEnvelope:
    """Enveloppe sure derivee du dernier palier sain (voir domain/
    calibration/validators.py::compute_envelope) — jamais calculee
    ailleurs, notamment jamais recalculee cote application/interfaces."""

    vu_safe: int
    rps_safe: int
    connections_safe: int
    margin_applied: float
    last_healthy_stage_id: str
    first_degraded_stage_id: str | None
    confidence: str


@dataclass(frozen=True, slots=True)
class CalibrationFingerprint:
    """Empreinte NON invasive de la machine (voir document produit,
    section "Persistance et compatibilite") — jamais d'adresse MAC ni de
    numero de serie materiel, uniquement des caracteristiques logicielles
    et des capacites mesurables. Cle de nommage du fichier de resultat
    persiste (infrastructure/calibration/fingerprint.py calcule un hash
    stable a partir de ces champs)."""

    schema_version: int
    engine_version: str
    python_version: str
    os_name: str
    architecture: str
    logical_cpu_count: int
    total_ram_mb: float | None
    open_files_soft_limit: int | None
    workers_mode: str
    scenario_id: str


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    """Resultat complet d'un calibrage, tel que persiste (voir ports/
    calibration_repository.py). envelope est None si meme le premier
    palier exploitable (idle_baseline ou calib_1) a echoue — un calibrage
    peut donc etre stocke et consulte sans jamais avoir produit
    d'enveloppe utilisable."""

    fingerprint: CalibrationFingerprint
    started_at: datetime
    duration_seconds: float
    stages: tuple[CalibrationStageResult, ...]
    envelope: CalibrationEnvelope | None
    overall_stop_reason: str | None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte les entites du sous-domaine calibration : definition d'un
#   palier (CalibrationStage), mesure/verdict d'un palier deja execute
#   (CalibrationStageResult), enveloppe sure derivee (CalibrationEnvelope),
#   identite de la machine (CalibrationFingerprint), resultat complet
#   persistable (CalibrationResult).
# Pourquoi dans domain/calibration/ (charte) :
# - Meme role que domain/load/models.py pour son propre sous-domaine :
#   entites/VO metier pures, aucune I/O, aucune dependance a psutil/
#   http.server/sqlite (voir infrastructure/calibration/ pour la mesure
#   reelle, ce fichier ne fait que porter le resultat deja mesure).
# Ce qu'il ne contient PAS :
# - Aucun seuil numerique (voir domain/calibration/policies.py).
# - Aucune logique d'evaluation sante/arret ni de calcul d'enveloppe (voir
#   domain/calibration/validators.py) : ce fichier reste des value objects
#   passifs.
# - Aucun sondage systeme reel (CPU/memoire/etc.) : les valeurs de
#   CalibrationStageResult sont deja agregees par l'appelant
#   (infrastructure/calibration/stage_runner.py) a partir de
#   domain/runs/models.py::SystemSnapshot, jamais mesurees ici.
# Points cles :
# - CalibrationFingerprint est deliberement plat (aucun champ imbrique) :
#   serialisation JSON directe sans mapping special, coherent avec
#   infrastructure/storage/files/json_calibration_store.py (memes
#   contraintes que json_settings_store.py).
# - CalibrationResult.envelope: CalibrationEnvelope | None (pas de valeur
#   par defaut factice type "enveloppe vide") : un calibrage qui echoue
#   des le premier palier reste un resultat PERSISTABLE et CONSULTABLE
#   (utile au diagnostic — "pourquoi mon calibrage echoue toujours ?"),
#   simplement sans enveloppe exploitable, jamais confondu avec un
#   calibrage jamais tente.
# - StageMeasurement importe SystemSnapshot (domain/runs/), un sous-domaine
#   deja existant : coherent, un palier de calibrage se mesure avec
#   exactement les memes primitives qu'un intervalle de run reel (meme
#   infrastructure/probe/live_probe.py::LiveSystemSampler des deux cotes).
# Comment il sera utilise (apercu) :
# - infrastructure/calibration/stage_runner.py construit StageMeasurement.
# - domain/calibration/validators.py::evaluate_stage_outcome() le
#   consomme pour produire CalibrationStageResult/CalibrationEnvelope.
# - infrastructure/calibration/fingerprint.py construit
#   CalibrationFingerprint.
# - application/commands/run_calibration.py assemble le CalibrationResult
#   final et le transmet a ports/calibration_repository.py.
#---------------------------------------------------------------------->
