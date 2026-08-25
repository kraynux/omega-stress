# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Hook : construit et emet les evenements d'audit d'un run."""
from __future__ import annotations

from collections.abc import Callable

from omega_stress.core.audit import AuditEvent
from omega_stress.domain.runs.models import LoadRun

AuditSink = Callable[[AuditEvent], None]
"""Destination d'un evenement d'audit, fournie par l'appelant (typiquement
infrastructure/logging/audit_logger.py::record en production, un fake en
test) — local a ce module, pas promu en shared/typing.py tant qu'un seul
fichier le consomme."""


def emit_run_started(run: LoadRun, *, sink: AuditSink) -> None:
    sink(
        AuditEvent(
            action="run_started",
            outcome="ok",
            authorized=True,
            detail=f"run={run.id} target={run.target_id} level={run.level.value}",
        )
    )


def emit_run_finished(run: LoadRun, *, sink: AuditSink) -> None:
    verdict = run.result.verdict.value if run.result is not None else "unknown"
    sink(
        AuditEvent(
            action="run_finished",
            outcome=verdict,
            authorized=True,
            detail=f"run={run.id}",
        )
    )


def emit_authorization_denied(target_id: str, *, sink: AuditSink) -> None:
    sink(
        AuditEvent(
            action="run_denied",
            outcome="unauthorized",
            authorized=False,
            detail=f"target={target_id}",
        )
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Construit des AuditEvent (core/audit.py) a des points cles du cycle de
#   vie d'un run, et les remet a un sink fourni par l'appelant.
# Pourquoi dans application/pipeline/hooks/ (charte) :
# - Point d'integration nomme du pipeline (ARCHITECTURE.md §4, etape 8),
#   sans dependance directe a un mecanisme de journalisation concret :
#   AuditSink reste une simple fonction, jamais un import
#   d'infrastructure/logging/ ici.
# Ce qu'il ne contient PAS :
# - Aucune ecriture disque (voir infrastructure/logging/audit_logger.py,
#   qui implemente le sink concret en production).
# - Aucun evenement pour les etapes intermediaires du pipeline (guards
#   individuels) : seuls demarrage, fin et refus d'autorisation sont
#   couverts en V1, les autres emissions (ex. arret automatique) restent a
#   ajouter si un besoin de tracabilite plus fin est confirme.
# Points cles :
# - AuditSink est defini localement ici (pas dans shared/typing.py) tant
#   qu'aucun deuxieme fichier n'en a besoin — coherent avec la regle
#   deja posee dans shared/typing.py.
# - emit_run_finished() lit run.result.verdict, jamais un parametre
#   verdict separe : source unique de verite, le LoadRun deja cloture
#   porte son propre verdict.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle emit_run_started()/
#   emit_run_finished().
# - application/pipeline/guards/authorization_guard.py (ou son appelant)
#   peut appeler emit_authorization_denied() en cas de refus.
#---------------------------------------------------------------------->
