# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Validation pure d'un LoadPlan et evaluation de seuil (sans I/O)."""
from __future__ import annotations

from collections.abc import Sequence

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import (
    PrecheckRequiredError,
    ThresholdExceededError,
    UnauthorizedTargetError,
    ValidationError,
)
from omega_stress.domain.load import policies
from omega_stress.domain.load.duration_presets import DurationPreset, duration_preset
from omega_stress.domain.load.models import LoadPlan, Thresholds
from omega_stress.domain.runs.models import IntervalSample, SystemSnapshot

PlanValidationError = ValidationError | UnauthorizedTargetError | PrecheckRequiredError


def validate_plan(plan: LoadPlan) -> Result[LoadPlan, PlanValidationError]:
    """Verifie qu'un LoadPlan est structurellement valide et respecte les
    politiques de bornage — ne verifie PAS l'etat reel du systeme
    (capacite locale, etc.), qui reste du ressort des guards applicatifs
    (application/pipeline/guards/, voir ARCHITECTURE.md §4)."""
    if not plan.target_authorization_confirmed:
        return Err(
            UnauthorizedTargetError(
                "Aucun run ne peut demarrer sans confirmation d'autorisation de la cible."
            )
        )

    if policies.is_precheck_mandatory(plan.level) and not plan.precheck_validated:
        return Err(
            PrecheckRequiredError(
                f"Le niveau {plan.level.value} exige un pre-check automatique valide "
                f"avant de demarrer."
            )
        )

    if plan.duration_preset_id is not None:
        preset = duration_preset(plan.duration_preset_id)
        if plan.family not in preset.compatible_families:
            return Err(
                ValidationError(
                    f"Le profil {preset.name} n'est pas compatible avec la famille "
                    f"{plan.family.value}."
                )
            )
        if plan.duration.minutes != preset.total_minutes:
            return Err(
                ValidationError(
                    f"Duree {plan.duration.minutes} min incoherente avec le profil "
                    f"{preset.name} ({preset.total_minutes} min attendues)."
                )
            )
        preset_result = evaluate_duration_preset(
            plan.level, preset, reinforced_confirmation_text=plan.reinforced_confirmation_text
        )
        if isinstance(preset_result, Err):
            return preset_result
    else:
        allowed = policies.allowed_durations_minutes(
            plan.level, extended_authorized=plan.precheck_validated
        )
        if plan.duration.minutes not in allowed:
            return Err(
                ValidationError(
                    f"Duree {plan.duration.minutes} min non autorisee "
                    f"pour le niveau {plan.level.value}."
                )
            )

    if plan.family is TestFamily.RAMP and not plan.ramp_steps:
        return Err(ValidationError("Un Test charge doit definir au moins une etape de rampe."))
    ramp_steps_allowed = plan.family is TestFamily.RAMP or (
        plan.family is TestFamily.CONNECTION and plan.duration_preset_id is not None
    )
    if not ramp_steps_allowed and plan.ramp_steps:
        return Err(
            ValidationError(
                "Seul un Test charge (ou un Test connexions avec profil de duree) "
                "peut definir des etapes de rampe."
            )
        )

    return Ok(plan)


def evaluate_threshold(
    *,
    observed_error_rate: float,
    observed_p95_latency_ms: float | None,
    thresholds: Thresholds,
) -> Result[None, ThresholdExceededError]:
    """Compare une mesure d'intervalle aux seuils d'arret. Appelee en
    continu par le pipeline pendant l'execution (ARCHITECTURE.md §4,
    guards/threshold_guard.py)."""
    if observed_error_rate > thresholds.max_error_rate:
        return Err(
            ThresholdExceededError(
                f"Taux d'erreur observe {observed_error_rate:.1%} > "
                f"seuil {thresholds.max_error_rate:.1%}"
            )
        )
    if (
        thresholds.max_p95_latency_ms is not None
        and observed_p95_latency_ms is not None
        and observed_p95_latency_ms > thresholds.max_p95_latency_ms
    ):
        return Err(
            ThresholdExceededError(
                f"Latence p95 observee {observed_p95_latency_ms:.0f}ms > "
                f"seuil {thresholds.max_p95_latency_ms:.0f}ms"
            )
        )
    return Ok(None)


def evaluate_duration_preset(
    level: IntensityLevel,
    preset: DurationPreset,
    *,
    reinforced_confirmation_text: str | None,
) -> Result[None, ValidationError]:
    """Verifie qu'un niveau est autorise pour un profil de duree D1-D6
    (mode "profil", domain/load/duration_presets.py) — une regle d'ACCES
    au niveau pour cette duree, distincte de evaluate_threshold() ci-dessus
    (seuils d'arret evalues PENDANT l'execution).

    - level <= preset.free_max_level (ordre de declaration d'IntensityLevel,
      voir core/enums.py) : autorise sans condition.
    - level == preset.reinforced_level : autorise SEULEMENT si
      reinforced_confirmation_text correspond exactement a
      policies.REINFORCED_CONFIRMATION_PHRASE.
    - tout niveau au-dela (ou reinforced_level absent) : jamais propose a
      cette duree, quel que soit le texte fourni.
    """
    ordered_levels = list(IntensityLevel)
    free_index = ordered_levels.index(preset.free_max_level)
    level_index = ordered_levels.index(level)

    if level_index <= free_index:
        return Ok(None)

    if preset.reinforced_level is not None and level is preset.reinforced_level:
        if reinforced_confirmation_text == policies.REINFORCED_CONFIRMATION_PHRASE:
            return Ok(None)
        return Err(
            ValidationError(
                f"Le niveau {level.value} pour le profil {preset.name} "
                f"({preset.total_minutes} min) exige la confirmation renforcee exacte."
            )
        )

    return Err(
        ValidationError(
            f"Le niveau {level.value} n'est pas propose pour le profil {preset.name} "
            f"({preset.total_minutes} min)."
        )
    )


def evaluate_sliding_window(
    samples: Sequence[IntervalSample], *, now_second: float
) -> Result[None, ThresholdExceededError]:
    """Evalue les taux de timeout/HTTP 5xx/erreurs totales sur une
    fenetre glissante de policies.SLIDING_WINDOW_SECONDS, PUIS sur une
    fenetre critique plus courte (policies.CRITICAL_WINDOW_SECONDS) —
    contrairement a evaluate_threshold() ci-dessus (un seul
    IntervalSample), regarde un historique : attrape une degradation qui
    reste sous le seuil par intervalle mais s'accumule sur la duree, et
    reagit plus vite a un pic recent concentre via la fenetre courte
    (Phase 2 garde-fous)."""
    window_result = _evaluate_window(
        [s for s in samples if s.at_second > now_second - policies.SLIDING_WINDOW_SECONDS],
        window_label=f"{policies.SLIDING_WINDOW_SECONDS:.0f}s",
    )
    if isinstance(window_result, Err):
        return window_result
    return _evaluate_window(
        [s for s in samples if s.at_second > now_second - policies.CRITICAL_WINDOW_SECONDS],
        window_label=f"{policies.CRITICAL_WINDOW_SECONDS:.0f}s critique",
    )


def _evaluate_window(
    window_samples: list[IntervalSample], *, window_label: str
) -> Result[None, ThresholdExceededError]:
    total_requests = sum(s.request_count for s in window_samples)
    if total_requests < policies.MINIMUM_REQUESTS_FOR_WINDOW_EVALUATION:
        return Ok(None)

    timeout_rate = sum(s.errors.timeout for s in window_samples) / total_requests
    if timeout_rate >= policies.WINDOW_TIMEOUT_RATE_ABORT_THRESHOLD:
        return Err(
            ThresholdExceededError(
                f"Taux de timeout {timeout_rate:.1%} sur fenetre {window_label} >= "
                f"seuil {policies.WINDOW_TIMEOUT_RATE_ABORT_THRESHOLD:.0%}",
                signal="window_timeout_rate_exceeded",
            )
        )

    http_5xx_rate = sum(s.errors.http_5xx for s in window_samples) / total_requests
    if http_5xx_rate >= policies.WINDOW_HTTP_5XX_RATE_ABORT_THRESHOLD:
        return Err(
            ThresholdExceededError(
                f"Taux d'erreurs HTTP 5xx {http_5xx_rate:.1%} sur fenetre {window_label} >= "
                f"seuil {policies.WINDOW_HTTP_5XX_RATE_ABORT_THRESHOLD:.0%}",
                signal="window_http_5xx_rate_exceeded",
            )
        )

    total_error_rate = sum(s.error_count for s in window_samples) / total_requests
    if total_error_rate >= policies.WINDOW_TOTAL_ERROR_RATE_ABORT_THRESHOLD:
        return Err(
            ThresholdExceededError(
                f"Taux d'erreurs total {total_error_rate:.1%} sur fenetre {window_label} >= "
                f"seuil {policies.WINDOW_TOTAL_ERROR_RATE_ABORT_THRESHOLD:.0%}",
                signal="window_error_rate_exceeded",
            )
        )
    return Ok(None)


def _single_core_abort_threshold(system: SystemSnapshot) -> float:
    """Seuil d'arret CPU generateur pour CE snapshot, relatif a ce qu'un
    seul coeur logique peut fournir sur CETTE machine (voir policies.py::
    GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE) — jamais un pourcentage
    absolu fixe. logical_cpu_count manquant (mesure ratee) retombe sur 1
    coeur (hypothese la plus conservatrice : seuil le plus bas possible,
    jamais le plus permissif)."""
    cores = system.logical_cpu_count if system.logical_cpu_count else 1
    return policies.GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE * (100.0 / cores)


def evaluate_generator_resources(
    samples: Sequence[IntervalSample],
) -> Result[None, ThresholdExceededError]:
    """Evalue les ressources locales du generateur (CPU/memoire/FDs,
    domain/runs/models.py::SystemSnapshot, Phase 1) contre les seuils
    d'arret de policies.py — jamais bloquant si la mesure a echoue
    (system=None) : une metrique manquante n'est jamais une raison
    d'arreter le run (Phase 2 garde-fous)."""
    if not samples:
        return Ok(None)
    latest = samples[-1]
    if latest.system is None:
        return Ok(None)

    sustained = samples[-policies.GENERATOR_CPU_ABORT_SUSTAINED_SAMPLES :]
    if len(sustained) == policies.GENERATOR_CPU_ABORT_SUSTAINED_SAMPLES and all(
        s.system is not None
        and s.system.cpu_percent_generator is not None
        and s.system.cpu_percent_generator >= _single_core_abort_threshold(s.system)
        and s.system.cpu_percent_global is not None
        and s.system.cpu_percent_global >= policies.GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_PERCENT
        for s in sustained
    ):
        threshold_text = f"{_single_core_abort_threshold(latest.system):.0f}%"
        return Err(
            ThresholdExceededError(
                f"CPU generateur >= {threshold_text} (~"
                f"{policies.GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE:.0%} d'un coeur) ET "
                f"CPU machine >= {policies.GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_PERCENT:.0f}% "
                f"pendant {policies.GENERATOR_CPU_ABORT_SUSTAINED_SAMPLES}s : la machine hote "
                f"elle-meme est sous pression, pas seulement le generateur",
                signal="generator_cpu_exceeded",
            )
        )

    if (
        latest.system.memory_available_percent is not None
        and latest.system.memory_available_percent
        < policies.MEMORY_AVAILABLE_ABORT_THRESHOLD_PERCENT
    ):
        return Err(
            ThresholdExceededError(
                f"Memoire disponible {latest.system.memory_available_percent:.0f}% < "
                f"seuil {policies.MEMORY_AVAILABLE_ABORT_THRESHOLD_PERCENT:.0f}%",
                signal="generator_memory_exceeded",
            )
        )

    if (
        latest.system.open_files is not None
        and latest.system.open_files_soft_limit is not None
        and latest.system.open_files_soft_limit > 0
        and (latest.system.open_files / latest.system.open_files_soft_limit)
        >= policies.OPEN_FILES_ABORT_RATIO
    ):
        return Err(
            ThresholdExceededError(
                f"Descripteurs de fichiers {latest.system.open_files}/"
                f"{latest.system.open_files_soft_limit} >= "
                f"{policies.OPEN_FILES_ABORT_RATIO:.0%} de la limite",
                signal="generator_fds_exceeded",
            )
        )

    return Ok(None)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - validate_plan() : validation structurelle pure d'un LoadPlan complet
#   (autorisation, pre-check, duree ou profil D1-D6, coherence family/
#   ramp_steps).
# - evaluate_threshold() : comparaison pure d'une mesure d'intervalle aux
#   seuils d'arret d'un plan, sans effet de bord.
# - evaluate_sliding_window() / evaluate_generator_resources() (Phase 2
#   garde-fous) : contrairement a evaluate_threshold() (un seul
#   IntervalSample), regardent un HISTORIQUE de samples — fenetres
#   glissantes 30s/10s pour les signaux cote cible, ressources locales
#   du generateur (CPU soutenu/memoire/FDs, Phase 1) pour les signaux
#   cote generateur. Seuils fixes de policies.py, jamais issus de
#   Thresholds (pas configurables par profil, voir policies.py).
# - evaluate_duration_preset() (2026-09-01, mode "profil" D1-D6) : regle
#   d'ACCES au niveau pour un profil de duree nomme — coexiste avec
#   allowed_durations_minutes() (mode manuel), jamais les deux a la fois
#   sur un meme plan (voir validate_plan()).
# Pourquoi dans domain/load/ (charte) :
# - Logique metier pure invoquee PAR les guards du pipeline applicatif
#   (application/pipeline/guards/), qui eux orchestrent l'I/O necessaire
#   (lecture de registre de capacite, etc.) — ce fichier ne fait jamais
#   cette orchestration lui-meme.
# Ce qu'il ne contient PAS :
# - Aucun acces a core/capability_registry.py (c'est
#   application/pipeline/guards/capability_guard.py qui le consulte).
# - Aucune boucle d'echantillonnage ni timer : evaluate_threshold() est
#   appelee une fois par mesure d'intervalle, pas une boucle elle-meme.
# Points cles :
# - validate_plan() retourne le PREMIER echec rencontre (autorisation,
#   puis pre-check, puis duree, puis coherence rampe) : ordre volontaire,
#   du controle le plus fondamental (autorisation) au plus specifique.
# - PlanValidationError est une union explicite plutot que DomainError
#   generique : permet a l'appelant de distinguer les trois cas sans
#   isinstance en cascade si besoin.
# - _single_core_abort_threshold() (2026-09-01, correction de bug reel) :
#   le seuil d'arret CPU generateur est desormais RELATIF au nombre de
#   coeurs logiques de la machine (policies.py::
#   GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE), jamais un pourcentage
#   absolu fixe — un moteur asyncio lie au GIL ne peut saturer qu'UN
#   SEUL coeur quel que soit le nombre de coeurs disponibles, un seuil
#   absolu de 90% etait donc systematiquement atteint sur 1-2 coeurs et
#   quasiment inatteignable des 4 (bug signale par un utilisateur en
#   test : run "Maximum" arrete au bout de 3s, diagnostic ">90%", alors
#   que l'utilisation globale machine restait ~20%). Necessaire car le
#   produit est destine a etre distribue sur des machines heterogenes —
#   le seuil doit rester significatif quel que soit le nombre de coeurs.
# - evaluate_generator_resources() exige desormais AUSSI cpu_percent_global
#   >= GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_PERCENT en plus du seuil CPU
#   generateur ci-dessus (2026-09-01, meme jour, second correctif suite a
#   une nouvelle session de test avec captures d'ecran) — ET, jamais OU :
#   voir domain/load/policies.py::GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_
#   PERCENT pour le diagnostic empirique complet (un test Connexions
#   normal sature legitimement ~22-25% de CPU generateur des le niveau
#   Moyen, meme sur une machine totalement saine). Le CPU generateur SEUL
#   ne suffit plus a arreter un test : il faut que la MACHINE ENTIERE
#   (cpu_percent_global) soit egalement sous pression au meme moment,
#   sinon aucune des deux conditions manquantes/insuffisantes ne
#   declenche d'arret (cpu_percent_global absent = jamais d'arret sur ce
#   critere, meme principe que "une metrique manquante n'est jamais une
#   raison d'arreter").
# Comment il sera utilise (apercu) :
# - application/pipeline/planner.py appelle validate_plan() avant de
#   construire le plan d'execution.
# - application/pipeline/guards/threshold_guard.py appelle
#   evaluate_threshold() a chaque point de mesure publie par le runner.
#---------------------------------------------------------------------->
