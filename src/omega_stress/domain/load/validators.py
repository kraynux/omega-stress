# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Validation pure d'un LoadPlan et evaluation de seuil (sans I/O)."""
from __future__ import annotations

from omega_stress.core.enums import TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import (
    PrecheckRequiredError,
    ThresholdExceededError,
    UnauthorizedTargetError,
    ValidationError,
)
from omega_stress.domain.load import policies
from omega_stress.domain.load.models import LoadPlan, Thresholds

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
    if plan.family is not TestFamily.RAMP and plan.ramp_steps:
        return Err(ValidationError("Seul un Test charge peut definir des etapes de rampe."))

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

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - validate_plan() : validation structurelle pure d'un LoadPlan complet
#   (autorisation, pre-check, duree, coherence family/ramp_steps).
# - evaluate_threshold() : comparaison pure d'une mesure d'intervalle aux
#   seuils d'arret d'un plan, sans effet de bord.
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
# Comment il sera utilise (apercu) :
# - application/pipeline/planner.py appelle validate_plan() avant de
#   construire le plan d'execution.
# - application/pipeline/guards/threshold_guard.py appelle
#   evaluate_threshold() a chaque point de mesure publie par le runner.
#---------------------------------------------------------------------->
