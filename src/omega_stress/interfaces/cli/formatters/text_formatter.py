# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Mise en forme texte/JSON des DTO pour la sortie CLI. Aucune decision metier."""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, cast

from omega_stress.application.dto.export_dto import ExportResultDTO
from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.application.dto.run_dto import RunDTO


def to_json(value: Any) -> str:
    """Serialise un DTO (ou une sequence de DTO) en JSON indente, pour le
    mode scriptable (--json, voir plan produit : "mode non interactif
    scriptable... couvrir les usages d'automatisation (cron, CI)")."""
    if is_dataclass(value) and not isinstance(value, type):
        payload: Any = asdict(cast(Any, value))
    elif isinstance(value, (tuple, list)):
        payload = [asdict(cast(Any, item)) if is_dataclass(item) else item for item in value]
    else:
        payload = value
    return json.dumps(payload, indent=2, ensure_ascii=False)


def format_profile(profile: ProfileDTO) -> str:
    status = "fige" if profile.frozen else "modifiable"
    threshold = f"erreur <= {profile.max_error_rate:.1%}"
    if profile.max_p95_latency_ms is not None:
        threshold += f", p95 <= {profile.max_p95_latency_ms:.0f}ms"
    lines = [
        f"Profil {profile.id} — {profile.name} ({status})",
        f"  Type       : {profile.family} / {profile.level}",
        f"  Duree      : {profile.duration_minutes} min",
        f"  Seuils     : {threshold}",
        f"  Cible      : {profile.default_target_id}",
        f"  Tags       : {', '.join(profile.tags) or '(aucun)'}",
        f"  Favori     : {'oui' if profile.favorite else 'non'}",
        f"  Archive    : {'oui' if profile.archived else 'non'}",
    ]
    return "\n".join(lines)


def format_profile_list(profiles: tuple[ProfileDTO, ...]) -> str:
    if not profiles:
        return "Aucun profil."
    return "\n".join(
        f"{p.id}  {p.name:<30}  {p.family}/{p.level}  "
        f"{'fige' if p.frozen else 'modifiable':<11}  {p.duration_minutes}min"
        for p in profiles
    )


def format_run(run: RunDTO) -> str:
    lines = [
        f"Run {run.id}",
        f"  Cible      : {run.target_address}",
        f"  Type       : {run.family} / {run.level}",
        f"  Demarre    : {run.started_at}",
    ]
    if run.finished_at is None:
        lines.append("  Statut     : en cours")
    else:
        lines.extend(
            [
                f"  Termine    : {run.finished_at}",
                f"  Verdict    : {run.verdict}",
                f"  Debit      : {run.observed_rate_per_minute} req/min",
                f"  Latence p95: {run.p95_latency_ms} ms",
                f"  Erreurs    : {run.error_count} / {run.total_requests}",
            ]
        )
        if run.events:
            lines.append(f"  Diagnostic : {run.events[-1].message}")
    return "\n".join(lines)


def format_run_list(runs: tuple[RunDTO, ...]) -> str:
    if not runs:
        return "Aucun run."
    return "\n".join(
        f"{r.id}  {r.started_at}  {r.family}/{r.level}  {r.verdict or 'en cours':<12}"
        for r in runs
    )


def format_export_result(result: ExportResultDTO) -> str:
    return f"Export {result.job_id} ecrit vers {result.written_path}"


def format_error(message: str) -> str:
    return f"Erreur : {message}"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Joue le role des `presenters` du TUI, mais pour une sortie texte/JSON
#   en console (ARCHITECTURE.md §2, description de interfaces/cli/).
# Pourquoi dans interfaces/cli/formatters/ (charte) :
# - Formatage seulement, aucune decision metier — chaque fonction lit un
#   DTO deja construit par application/, elle ne le recalcule jamais.
# Ce qu'il ne contient PAS :
# - Aucun import `textual` (interdit dans interfaces/cli/, verifie par le
#   contrat import-linter "textual seulement dans interfaces.tui").
# - Aucun format_terminal_status()/format_theme_status() : aucun command
#   CLI declare (run/profile/history/export) n'utilise ces DTO en V1 —
#   pas de fonction ecrite pour un besoin qui n'existe pas encore.
# Points cles :
# - to_json() est generique (dataclasses.asdict()) : fonctionne pour
#   n'importe quel DTO ou tuple de DTO sans fonction dediee par type,
#   utilise par tous les commands quand --json est demande.
# - Les fonctions format_* produisent un texte MULTI-LIGNES pour le detail
#   d'un objet, une LIGNE PAR ELEMENT pour une liste — convention
#   coherente avec les outils CLI Unix habituels (un objet = un bloc, une
#   liste = un flux grep-able).
# Comment il sera utilise (apercu) :
# - interfaces/cli/commands/*.py appellent une fonction format_* puis
#   impriment son resultat, sauf si --json est passe (auquel cas
#   to_json() est utilisee a la place).
#---------------------------------------------------------------------->
