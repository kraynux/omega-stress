# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : libelles humains pour l'affichage d'un resultat de calibrage."""
from __future__ import annotations

from datetime import datetime

from omega_stress.core.enums import TestFamily
from omega_stress.domain.calibration.models import CalibrationResult
from omega_stress.domain.calibration.policies import (
    CALIBRATION_STAGES,
    CALIBRATION_VALIDITY_DAYS_MANDATORY,
    CALIBRATION_VALIDITY_DAYS_RECOMMENDED,
)

_STAGE_NAMES: dict[str, str] = {stage.id: stage.name for stage in CALIBRATION_STAGES}


def envelope_summary(result: CalibrationResult) -> str:
    """Resume court de l'enveloppe sure, ou un message explicite si aucune
    enveloppe n'a pu etre calculee (le premier palier exploitable a deja
    echoue — voir domain/calibration/models.py::CalibrationResult.envelope)."""
    if result.envelope is None:
        reason = result.overall_stop_reason or "echec precoce"
        return f"Aucune enveloppe exploitable ({reason})."
    envelope = result.envelope
    last_healthy_name = _STAGE_NAMES.get(
        envelope.last_healthy_stage_id, envelope.last_healthy_stage_id
    )
    return (
        f"VU_safe {envelope.vu_safe} | RPS_safe {envelope.rps_safe} | "
        f"confiance {envelope.confidence} (dernier palier sain : {last_healthy_name})"
    )


def age_reminder(result: CalibrationResult, *, now: datetime) -> str:
    """Rappel d'age du calibrage, avec alerte au-dela des seuils
    recommande/obligatoire (document produit, "Calibrage unique et
    persistant") — affichage seul, aucun blocage applicatif (angle mort
    assume de ce chantier, voir plan)."""
    age_days = (now - result.started_at).days
    plural = "s" if age_days != 1 else ""
    if age_days >= CALIBRATION_VALIDITY_DAYS_MANDATORY:
        return (
            f"Calibrage vieux de {age_days} jour{plural} — renouvellement "
            f"OBLIGATOIRE (> {CALIBRATION_VALIDITY_DAYS_MANDATORY}j)."
        )
    if age_days >= CALIBRATION_VALIDITY_DAYS_RECOMMENDED:
        return (
            f"Calibrage vieux de {age_days} jour{plural} — renouvellement "
            f"recommande (> {CALIBRATION_VALIDITY_DAYS_RECOMMENDED}j)."
        )
    return f"Calibrage vieux de {age_days} jour{plural}."


def envelope_comparison_message(
    *, family: TestFamily, target_value: float, unit: str, result: CalibrationResult | None
) -> str:
    """Compare la valeur ciblee par le niveau choisi (connexions
    simultanees, requetes/s...) a l'enveloppe sure du dernier calibrage
    exploitable — affiche quand l'utilisateur decoche le mode securite
    (screens/request_panel.py et consorts), jamais pour plafonner ou
    bloquer quoi que ce soit (le chantier "application de l'enveloppe"
    reste deliberement differe, voir plan). Purement informatif : la
    responsabilite d'aller au-dela reste explicitement celle de
    l'utilisateur."""
    if result is None or result.envelope is None:
        return (
            "Aucun calibrage exploitable pour cette machine — vous ne connaissez pas ses "
            "limites reelles. Nous recommandons d'en faire un depuis l'ecran Calibrage avant "
            "de desactiver le mode securite sur un niveau intensif. Vous choisissez de "
            "depasser les garde-fous de CETTE machine : la fiabilite du resultat et la "
            "stabilite de votre ordinateur restent sous votre responsabilite."
        )
    envelope = result.envelope
    safe_value = envelope.connections_safe if family is TestFamily.CONNECTION else envelope.rps_safe
    comparison = "AU-DESSUS" if target_value > safe_value else "en dessous"
    return (
        f"Dernier calibrage : {safe_value} {unit} juges surs pour cette machine "
        f"(confiance {envelope.confidence}). Ce niveau vise {target_value:.0f} {unit} — "
        f"{comparison} de cette enveloppe. Au-dela, la fiabilite du resultat (nombre de "
        f"connexions/requetes/charge reellement atteint) peut baisser, et votre machine "
        f"pourrait ralentir ou geler temporairement : c'est votre responsabilite."
    )


def stage_lines(result: CalibrationResult) -> tuple[str, ...]:
    """Une ligne par palier deja execute : nom, debit atteint/cible, verdict."""
    lines = []
    for stage_result in result.stages:
        name = _STAGE_NAMES.get(stage_result.stage_id, stage_result.stage_id)
        status = "sain" if stage_result.is_healthy else "degrade"
        reason = f" — {stage_result.stop_reason}" if stage_result.stop_reason else ""
        lines.append(
            f"{name} : {stage_result.rps_achieved:.0f}/{stage_result.rps_target} req/s "
            f"({status}{reason})"
        )
    return tuple(lines)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit un CalibrationResult (domain/calibration/models.py) en texte
#   pret pour l'affichage : resume d'enveloppe, rappel d'age, une ligne
#   par palier execute.
# Pourquoi dans interfaces/tui/presenters/ (charte) :
# - Meme role que presenters/run_presenter.py pour son propre sous-domaine :
#   aucune decision metier, seulement du formatage d'une donnee deja
#   calculee par domain/calibration/validators.py.
# Ce qu'il ne contient PAS :
# - Aucun calcul d'enveloppe/sante (deja fige dans le CalibrationResult
#   recu) : ce module ne fait que le mettre en mots.
# Points cles :
# - _STAGE_NAMES : CalibrationStageResult ne porte que stage_id (voir son
#   propre INFO DEV, domain/calibration/models.py), jamais le nom lisible
#   du palier — retrouve ici via policies.py::CALIBRATION_STAGES, source
#   de verite unique de l'ordre/nom des paliers.
# - age_reminder() prend `now` en parametre explicite (pas datetime.now()
#   interne) : coherent avec shared/typing.py::Clock, teste sans horloge
#   reelle si besoin, meme convention que le reste du projet.
# - CalibrationResult est consomme ICI directement (pas de DTO
#   intermediaire type RunDTO) : deja le choix fait cote application/
#   commands/run_calibration.py (retourne Result[CalibrationResult, ...]
#   brut plutot qu'un DTO), ce presenter suit la meme convention plutot
#   que d'introduire une couche DTO a moitie pour ce seul sous-domaine.
# - envelope_comparison_message() (2026-09-01, "mode securite" a cocher,
#   demande explicite de l'utilisateur) : lie le calibrage (mesure) au
#   choix de desactiver le mode securite (execution) SANS jamais les
#   coupler automatiquement — decision explicite de l'utilisateur (pas de
#   plafonnement, pas de blocage meme sans calibrage exploitable),
#   uniquement une information au bon moment. `unit`/`target_value` sont
#   fournis par l'appelant (deja disponibles via domain/load/presets.py
#   dans les 3 ecrans de lancement), ce presenter ne resout jamais lui-
#   meme quelle valeur comparer depuis family/level.
# Comment il sera utilise :
# - screens/calibration_screen.py (consultation du dernier resultat connu
#   et affichage de la progression apres un nouveau calibrage).
# - screens/{request_panel,connection_panel,ramp_panel}.py (comparaison
#   affichee des que "Mode securite" est decoche).
#---------------------------------------------------------------------->
