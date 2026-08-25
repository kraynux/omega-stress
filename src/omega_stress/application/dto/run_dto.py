# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""DTO expose a la presentation pour un Run."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunEventDTO:
    """Vue plate d'un RunEvent (domain/runs/models.py), tel qu'attache a
    un RunDTO."""

    occurred_at: str
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class IntervalSampleDTO:
    """Vue plate d'un IntervalSample (domain/runs/models.py), tel
    qu'attache a un RunDTO — memes champs, meme ordre, aucune conversion."""

    at_second: float
    observed_rate_per_minute: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_count: int
    request_count: int


@dataclass(frozen=True, slots=True)
class RunDTO:
    """Vue plate d'un LoadRun, en cours ou termine. Les champs de resultat
    restent None tant que le run n'est pas termine."""

    id: str
    profile_id: str | None
    target_id: str
    target_address: str
    family: str
    level: str
    started_at: str
    finished_at: str | None
    verdict: str | None
    observed_rate_per_minute: float | None
    p95_latency_ms: float | None
    error_count: int | None
    total_requests: int | None
    events: tuple[RunEventDTO, ...] = ()
    sample_count: int = 0
    samples: tuple[IntervalSampleDTO, ...] = ()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Forme plate d'un LoadRun, aplatissant son LoadResult optionnel dans
#   les memes champs plutot que d'imbriquer un sous-DTO.
# Pourquoi dans application/dto/ (charte) :
# - Objet de transfert : la presentation lit des champs simples, sans
#   avoir a tester `run.result is not None` elle-meme a chaque acces.
# Ce qu'il ne contient PAS :
# - Aucun champ p50/p99 (seul p95 est retenu pour l'affichage synthetique
#   de liste) : le detail complet (p50/p99, paliers) reste dans
#   ReportContent, construit separement pour l'export d'un run
#   (application/commands/export_run_report.py), sans alourdir ce DTO de
#   liste.
# Points cles :
# - Tous les champs de resultat sont None ensemble pour un run en cours
#   (finished_at is None <=> verdict is None <=> ...) : invariant garanti
#   par application/dto/mappers.py::run_to_dto(), pas par ce DTO
#   lui-meme.
# - target_address (2026-08-25, distinct de target_id) : bug reel rapporte
#   ("si on choisit une epingle... on a pas le nom, on a le numero
#   657000045dbgr4100346... comment savoir c'est quelle cible ?") —
#   target_id est un identifiant STABLE (utile pour filtrer/relier des
#   runs a la meme cible), mais reste un id OPAQUE genere par
#   shared/ids.py::new_id() pour une cible epinglee (voir
#   application/commands/pin_target.py) : illisible tel quel a l'ecran.
#   target_address est l'adresse humaine correspondante
#   (TargetAddress.base_url), resolue par l'appelant (query/command, qui a
#   acces au repository — voir application/dto/mappers.py::run_to_dto(),
#   ce DTO/mapper restent purs, aucune resolution ici). Pour une cible
#   manuelle jamais epinglee, target_id EST deja l'URL brute (voir
#   screens/request_panel.py::_resolve_target()) : dans ce cas
#   target_address vaut la meme chaine que target_id, jamais vide.
# - events (2026-08-24) : relai direct de LoadResult.events (RunEvent),
#   pas un sous-ensemble de ReportContent — juste assez pour qu'un ecran
#   de lancement ou de detail affiche LA raison d'un echec/arret
#   automatique (dernier evenement), sans construire le ReportDiagnostic
#   complet (recommandations, box resume) qui reste reserve a l'export.
#   Vide par defaut : un run en cours ou reussi n'a jamais d'evenement.
# - sample_count : compte rapide (longueur de `samples`), garde par
#   commodite pour les ecrans qui n'ont besoin que du nombre (widgets/
#   history_table.py, interfaces/cli/formatters/text_formatter.py) sans
#   payer la construction du tuple complet dans leur propre code d'appel.
# - samples (2026-08-24, revient sur la decision initiale ci-dessus qui
#   l'excluait) : demande explicite d'une chronologie visible directement
#   dans le TUI (screens/run_details.py, mini barres ASCII par intervalle)
#   sans repasser par un export — la decision "jamais deroule a l'ecran"
#   ne tenait plus une fois ce besoin exprime. Reste un miroir plat de
#   LoadResult.samples (IntervalSampleDTO), aucune agregation ici : le
#   regroupement par paliers pour l'affichage (si sample_count depasse la
#   hauteur d'ecran raisonnable) est fait par
#   interfaces/tui/presenters/run_presenter.py::chronology_lines(), pas
#   par ce DTO.
# Comment il sera utilise (apercu) :
# - application/dto/mappers.py::run_to_dto().
# - interfaces/tui/widgets/history_table.py (colonne "Cible", via
#   target_address), interfaces/cli/formatters/text_formatter.py
#   (sample_count, target_address).
# - interfaces/tui/screens/run_details.py (target_address dans le
#   resume), via presenters/run_presenter.py::chronology_lines()
#   (samples).
#---------------------------------------------------------------------->
