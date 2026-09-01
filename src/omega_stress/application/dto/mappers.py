# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Conversion entites de domaine <-> DTO, dans les deux sens ou l'exposition l'exige."""
from __future__ import annotations

from omega_lib.terminal.models import TerminalProfile
from omega_lib.theme.models import AppliedTheme

from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.application.dto.run_dto import IntervalSampleDTO, RunDTO, RunEventDTO
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.application.dto.terminal_dto import TerminalStatusDTO
from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.runs.models import LoadRun
from omega_stress.domain.targets.models import PinnedTarget, Target


def profile_to_dto(profile: Profile) -> ProfileDTO:
    return ProfileDTO(
        id=profile.id,
        name=profile.name,
        description=profile.description,
        default_target_id=profile.default_target_id,
        family=profile.family.value,
        level=profile.level.value,
        duration_minutes=profile.duration.minutes,
        max_error_rate=profile.thresholds.max_error_rate,
        max_p95_latency_ms=profile.thresholds.max_p95_latency_ms,
        tags=profile.tags,
        extended_duration_authorized=profile.extended_duration_authorized,
        frozen=profile.frozen,
        favorite=profile.favorite,
        archived=profile.archived,
        created_at=profile.created_at.isoformat(),
        frozen_at=profile.frozen_at.isoformat() if profile.frozen_at is not None else None,
    )


def target_to_dto(target: Target, *, pinned: bool) -> TargetDTO:
    return TargetDTO(
        id=target.id,
        base_url=target.address.base_url,
        tags=target.tags,
        notes=target.notes,
        pinned=pinned,
        last_used_at=target.last_used_at.isoformat() if target.last_used_at is not None else None,
    )


def pinned_target_to_dto(pinned: PinnedTarget) -> TargetDTO:
    return target_to_dto(pinned.target, pinned=True)


def run_to_dto(run: LoadRun, *, target_address: str) -> RunDTO:
    result = run.result
    events = (
        tuple(
            RunEventDTO(occurred_at=e.occurred_at.isoformat(), kind=e.kind, message=e.message)
            for e in result.events
        )
        if result is not None
        else ()
    )
    samples = (
        tuple(
            IntervalSampleDTO(
                at_second=s.at_second,
                observed_rate_per_minute=s.observed_rate_per_minute,
                p50_latency_ms=s.p50_latency_ms,
                p95_latency_ms=s.p95_latency_ms,
                p99_latency_ms=s.p99_latency_ms,
                error_count=s.error_count,
                request_count=s.request_count,
            )
            for s in result.samples
        )
        if result is not None
        else ()
    )
    return RunDTO(
        id=run.id,
        profile_id=run.profile_id,
        target_id=run.target_id,
        target_address=target_address,
        family=run.family.value,
        level=run.level.value,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat() if run.finished_at is not None else None,
        verdict=result.verdict.value if result is not None else None,
        observed_rate_per_minute=result.observed_rate_per_minute if result is not None else None,
        p95_latency_ms=result.p95_latency_ms if result is not None else None,
        error_count=result.error_count if result is not None else None,
        total_requests=result.total_requests if result is not None else None,
        events=events,
        sample_count=len(result.samples) if result is not None else 0,
        samples=samples,
        errors_timeout=result.errors.timeout if result is not None else 0,
        errors_connection=result.errors.connection if result is not None else 0,
        errors_http_4xx=result.errors.http_4xx if result is not None else 0,
        errors_http_5xx=result.errors.http_5xx if result is not None else 0,
        errors_other=result.errors.other if result is not None else 0,
        peak_cpu_percent_generator=(
            result.peak_cpu_percent_generator if result is not None else None
        ),
        peak_memory_rss_mb=result.peak_memory_rss_mb if result is not None else None,
    )


def terminal_profile_to_dto(profile: TerminalProfile) -> TerminalStatusDTO:
    return TerminalStatusDTO(
        family=profile.signals.family,
        columns=profile.signals.columns,
        rows=profile.signals.rows,
        render_profile=profile.render_profile.value,
    )


def applied_theme_to_dto(applied: AppliedTheme) -> ThemeStatusDTO:
    return ThemeStatusDTO(
        theme_name=applied.theme_name,
        render_profile=applied.render_profile.value,
        fell_back_from=applied.fell_back_from,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul endroit du projet ou une entite/VO de domain/ est lue pour
#   produire un DTO d'application/dto/ — aucun command/query ne fait cette
#   conversion lui-meme.
# Pourquoi dans application/dto/ (charte) :
# - Fonctions de mapping pures, sans I/O, consommees par les commands et
#   queries juste avant de retourner un resultat a la presentation.
# Ce qu'il ne contient PAS :
# - Aucun mapping inverse DTO -> entite domaine : les commands construisent
#   leurs entites domaine directement depuis des parametres primitifs
#   (voir application/commands/create_profile.py), jamais depuis un DTO
#   reinjecte — un DTO est une sortie vers la presentation, pas une entree
#   generique.
# - Aucune logique de decision (choix de theme, calcul de profil de
#   rendu...) : uniquement de la mise a plat de donnees deja decidees.
# Points cles :
# - Toutes les dates sont serialisees en ISO 8601 ici, au point unique de
#   sortie vers la presentation — jamais reformatees plus loin.
# - pinned_target_to_dto() delegue a target_to_dto(pinned=True) plutot que
#   de dupliquer la construction : une seule source de verite pour la
#   forme du TargetDTO.
# - run_to_dto() : samples (2026-08-24) suit exactement le meme patron que
#   events juste au-dessus (tuple vide si result is None, sinon mappe un a
#   un) — voir application/dto/run_dto.py pour la raison de cet ajout.
# - run_to_dto(target_address=...) (2026-08-25) : SEUL parametre non
#   derive de `run` lui-meme — resoudre une adresse humaine depuis
#   run.target_id exige un TargetRepository (I/O), que ce mapper pur ne
#   doit jamais toucher (voir "Ce qu'il ne contient PAS" plus haut).
#   L'appelant (application/commands/_launch_support.py, run_precheck.py :
#   deja en possession de l'URL demandee, aucune resolution necessaire ;
#   application/queries/get_run_details.py, list_history.py : resolvent
#   via target_repository.get()) reste responsable de la resoudre avant
#   d'appeler cette fonction — voir application/dto/run_dto.py pour la
#   justification complete du champ.
# Comment il sera utilise (apercu) :
# - Chaque query/command de application/ qui retourne un DTO appelle une
#   des fonctions de ce fichier en derniere etape.
#---------------------------------------------------------------------->
