# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Validation pure des preconditions de calibrage, evaluation d'un palier
deja execute (sante/arret), et calcul de l'enveloppe sure — sans I/O."""
from __future__ import annotations

from collections.abc import Sequence

from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.calibration import policies
from omega_stress.domain.calibration.exceptions import CalibrationPreconditionError
from omega_stress.domain.calibration.models import (
    CalibrationEnvelope,
    CalibrationStage,
    CalibrationStageResult,
)
from omega_stress.domain.runs.models import SystemSnapshot


def evaluate_preconditions(
    *,
    cpu_global_percent: float | None,
    memory_available_percent: float | None,
    swap_active_or_growing: bool,
    load_average_1min: float | None,
    logical_cpu_count: int,
    another_calibration_or_run_active: bool,
) -> Result[None, CalibrationPreconditionError]:
    """Verifie que la machine n'est pas deja sous forte pression avant de
    demarrer un calibrage (document : "un calibrage realise sur une
    machine deja chargee serait inutilisable ou artificiellement
    faible"). N'inclut PAS la precondition "port local de calibrage
    indisponible" du document : le serveur local se lie sur un port
    ephemere choisi par l'OS (infrastructure/calibration/local_server.py),
    ce cas ne peut normalement pas se produire."""
    if another_calibration_or_run_active:
        return Err(
            CalibrationPreconditionError(
                "Un calibrage ou un test est deja en cours sur ce poste."
            )
        )
    if (
        cpu_global_percent is not None
        and cpu_global_percent > policies.CALIBRATION_PRECONDITION_CPU_GLOBAL_MAX_PERCENT
    ):
        return Err(
            CalibrationPreconditionError(
                f"CPU global {cpu_global_percent:.0f}% > seuil "
                f"{policies.CALIBRATION_PRECONDITION_CPU_GLOBAL_MAX_PERCENT:.0f}% : "
                f"machine deja sous pression."
            )
        )
    if (
        memory_available_percent is not None
        and memory_available_percent
        < policies.CALIBRATION_PRECONDITION_MEMORY_AVAILABLE_MIN_PERCENT
    ):
        return Err(
            CalibrationPreconditionError(
                f"Memoire disponible {memory_available_percent:.0f}% < seuil "
                f"{policies.CALIBRATION_PRECONDITION_MEMORY_AVAILABLE_MIN_PERCENT:.0f}%."
            )
        )
    if swap_active_or_growing:
        return Err(
            CalibrationPreconditionError(
                "Swap deja active ou en croissance : machine deja sous pression."
            )
        )
    if load_average_1min is not None and load_average_1min > logical_cpu_count:
        return Err(
            CalibrationPreconditionError(
                f"Load average 1 min {load_average_1min:.1f} > {logical_cpu_count} "
                f"coeurs logiques."
            )
        )
    return Ok(None)


def _peak(values: Sequence[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return max(present) if present else None


def _minimum(values: Sequence[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return min(present) if present else None


def _latest_logical_cpu_count(system_samples: Sequence[SystemSnapshot]) -> int:
    for sample in reversed(system_samples):
        if sample.logical_cpu_count:
            return sample.logical_cpu_count
    return 1


def _sustained_cpu_stop(
    system_samples: Sequence[SystemSnapshot], *, logical_cpu_count: int
) -> bool:
    """CPU generateur au-dela du ratio d'arret pendant
    CALIBRATION_STOP_SUSTAINED_SECONDS echantillons CONSECUTIFS — jamais
    un seul pic isole, meme patron que domain/load/validators.py::
    evaluate_generator_resources(). Condition NECESSAIRE mais PAS
    SUFFISANTE (2026-09-01) : evaluate_stage_outcome() n'arrete un
    palier que si _sustained_global_cpu_stop() est AUSSI vraie en meme
    temps (ET, jamais OU) — une saturation normale d'un seul coeur ne
    doit plus jamais, a elle seule, arreter un calibrage."""
    window = system_samples[-policies.CALIBRATION_STOP_SUSTAINED_SECONDS :]
    if len(window) < policies.CALIBRATION_STOP_SUSTAINED_SECONDS:
        return False
    threshold = policies.CALIBRATION_STOP_CPU_GENERATOR_MIN_RATIO_OF_SINGLE_CORE * (
        100.0 / logical_cpu_count
    )
    return all(
        s.cpu_percent_generator is not None and s.cpu_percent_generator >= threshold
        for s in window
    )


def _sustained_global_cpu_stop(system_samples: Sequence[SystemSnapshot]) -> bool:
    window = system_samples[-policies.CALIBRATION_STOP_SUSTAINED_SECONDS :]
    if len(window) < policies.CALIBRATION_STOP_SUSTAINED_SECONDS:
        return False
    return all(
        s.cpu_percent_global is not None
        and s.cpu_percent_global >= policies.CALIBRATION_STOP_CPU_GLOBAL_MIN_PERCENT
        for s in window
    )


def evaluate_stage_outcome(
    stage: CalibrationStage,
    *,
    rps_achieved: float,
    error_rate: float,
    system_samples: Sequence[SystemSnapshot],
    consecutive_timeouts: int,
    previous_stage_rps_below_ratio: bool,
) -> CalibrationStageResult:
    """Evalue un palier deja execute : verifie D'ABORD les criteres
    d'arret (document, table "Passage ou arret" — les plus severes),
    puis la sante SEULEMENT si aucun arret n'est declenche. Un palier
    peut etre "pas sain" sans pour autant declencher d'arret (ex. RPS
    legerement sous le ratio de sante sur ce seul palier) : la
    progression peut continuer, mais la confiance de l'enveloppe finale
    en tiendra compte (voir compute_envelope()).

    previous_stage_rps_below_ratio : True si le palier IMMEDIATEMENT
    PRECEDENT avait deja un ratio RPS sous CALIBRATION_STOP_RPS_ACHIEVED
    _RATIO_MAX — combine au ratio de CE palier pour detecter "deux
    paliers CONSECUTIFS" (document), jamais un simple compteur global."""
    logical_cpu_count = _latest_logical_cpu_count(system_samples)
    peak_cpu_generator = _peak([s.cpu_percent_generator for s in system_samples])
    peak_cpu_global = _peak([s.cpu_percent_global for s in system_samples])
    memory_min = _minimum([s.memory_available_percent for s in system_samples])
    rps_ratio = rps_achieved / stage.rps_target if stage.rps_target > 0 else 1.0

    stop_reason: str | None = None
    if _sustained_cpu_stop(
        system_samples, logical_cpu_count=logical_cpu_count
    ) and _sustained_global_cpu_stop(system_samples):
        stop_reason = "generator_cpu_sustained"
    elif (
        memory_min is not None
        and memory_min <= policies.CALIBRATION_STOP_MEMORY_AVAILABLE_MAX_PERCENT
    ):
        stop_reason = "memory_available_low"
    elif error_rate >= policies.CALIBRATION_STOP_ERROR_RATE_MIN:
        stop_reason = "error_rate_high"
    elif consecutive_timeouts >= policies.CALIBRATION_STOP_CONSECUTIVE_TIMEOUTS:
        stop_reason = "consecutive_timeouts"
    elif (
        previous_stage_rps_below_ratio
        and rps_ratio < policies.CALIBRATION_STOP_RPS_ACHIEVED_RATIO_MAX
    ):
        stop_reason = "rps_achieved_low_consecutive_stages"

    is_healthy = stop_reason is None and (
        (peak_cpu_generator is None
         or peak_cpu_generator
         < policies.CALIBRATION_HEALTHY_CPU_GENERATOR_MAX_RATIO_OF_SINGLE_CORE
         * (100.0 / logical_cpu_count))
        and (peak_cpu_global is None
             or peak_cpu_global < policies.CALIBRATION_HEALTHY_CPU_GLOBAL_MAX_PERCENT)
        and (memory_min is None
             or memory_min > policies.CALIBRATION_HEALTHY_MEMORY_AVAILABLE_MIN_PERCENT)
        and error_rate < policies.CALIBRATION_HEALTHY_ERROR_RATE_MAX
        and rps_ratio >= policies.CALIBRATION_HEALTHY_RPS_ACHIEVED_RATIO_MIN
    )

    return CalibrationStageResult(
        stage_id=stage.id,
        vu_target=stage.vu_target,
        rps_target=stage.rps_target,
        rps_achieved=rps_achieved,
        error_rate=error_rate,
        peak_cpu_percent_generator=peak_cpu_generator,
        peak_cpu_percent_global=peak_cpu_global,
        memory_available_percent_min=memory_min,
        is_healthy=is_healthy,
        stop_reason=stop_reason,
    )


_CONFIDENCE_BY_STAGE_INDEX: dict[int, str] = {0: "faible", 1: "faible", 2: "moyenne", 3: "moyenne"}
"""Index 0-based dans policies.CALIBRATION_STAGES du dernier palier sain
-> niveau de confiance. Index >= 4 (calib_4 et au-dela) -> "elevee"
(valeur par defaut ci-dessous). Seuils non donnes par le document,
choix retenu ici : plus la progression va loin sans etre stoppee, plus
l'enveloppe deduite est fiable."""


def compute_envelope(
    healthy_stage_results: Sequence[CalibrationStageResult],
    *,
    first_degraded_stage_id: str | None,
) -> CalibrationEnvelope | None:
    """Deduit l'enveloppe sure du dernier palier SAIN de la sequence
    (deja filtree/ordonnee par l'appelant — ce module ne connait pas
    l'ordre de policies.CALIBRATION_STAGES). None si healthy_stage_results
    est vide (meme idle_baseline/calib_1 n'a jamais ete sain)."""
    if not healthy_stage_results:
        return None
    last_healthy = healthy_stage_results[-1]
    stage_ids = [s.id for s in policies.CALIBRATION_STAGES]
    stage_index = (
        stage_ids.index(last_healthy.stage_id) if last_healthy.stage_id in stage_ids else 0
    )
    confidence = _CONFIDENCE_BY_STAGE_INDEX.get(stage_index, "elevee")

    vu_safe = int(last_healthy.vu_target * policies.CALIBRATION_SAFETY_MARGIN)
    rps_safe = int(last_healthy.rps_achieved * policies.CALIBRATION_SAFETY_MARGIN)

    return CalibrationEnvelope(
        vu_safe=vu_safe,
        rps_safe=rps_safe,
        connections_safe=vu_safe,
        margin_applied=policies.CALIBRATION_SAFETY_MARGIN,
        last_healthy_stage_id=last_healthy.stage_id,
        first_degraded_stage_id=first_degraded_stage_id,
        confidence=confidence,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - evaluate_preconditions() : verification pure des 4 preconditions
#   chiffrees du document avant de demarrer un calibrage.
# - evaluate_stage_outcome() : verdict sante/arret d'UN palier deja
#   execute, a partir de ses metriques deja agregees par l'appelant.
# - compute_envelope() : deduit VU_safe/RPS_safe/confiance du dernier
#   palier sain.
# Pourquoi dans domain/calibration/ (charte) :
# - Logique metier pure, aucune I/O, aucun sondage — meme role que
#   domain/load/validators.py pour son propre sous-domaine.
# Ce qu'il ne contient PAS :
# - Aucun sondage systeme reel, aucun appel HTTP, aucune boucle
#   temporelle : ces fonctions recoivent des mesures DEJA collectees
#   (voir infrastructure/calibration/stage_runner.py).
# - Aucune persistance (voir ports/calibration_repository.py).
# Points cles :
# - evaluate_stage_outcome() verifie les criteres D'ARRET avant la SANTE
#   (ordre volontaire, symetrique a domain/load/validators.py::
#   validate_plan() qui retourne aussi le PREMIER echec le plus
#   fondamental) : un palier peut echouer les deux verifications, seul
#   stop_reason importe alors pour la suite de la progression.
# - Seuils CPU generateur (sante et arret) relatifs a UN SEUL coeur des
#   leur premiere version (voir policies.py) — la normalisation par
#   coeur n'a donc jamais eu besoin d'etre corrigee ici. En revanche les
#   VALEURS de ratio elles-memes (0.80/0.85 a l'origine) se sont averees
#   trop basses en pratique (meme diagnostic empirique que domain/load/
#   policies.py::GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE, corrige le
#   meme jour) et le critere d'ARRET etait un OU entre generateur et
#   global plutot qu'un ET — les deux corriges le 2026-09-01 (ratios
#   releves a 0.90/0.95, _sustained_cpu_stop() ET _sustained_global_
#   cpu_stop() desormais exigees ensemble dans evaluate_stage_outcome()).
# - "RPS reel plafonne alors que les objectifs augmentent fortement"
#   (document) n'est PAS implemente : condition qualitative sans seuil
#   chiffre donne par le document — angle mort assume (voir plan).
# - compute_envelope() : vu_safe/rps_safe utilisent int() (troncature),
#   jamais round() — coherent avec la formule du document (floor()
#   explicite : "VU_safe = floor(VU_stable * marge)").
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py appelle les trois fonctions
#   dans l'ordre (preconditions -> paliers un par un -> enveloppe finale).
#---------------------------------------------------------------------->
