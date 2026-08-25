# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecriture des evenements d'audit en JSON structure (une ligne par evenement)."""
from __future__ import annotations

import json
from pathlib import Path

from omega_stress.core.audit import AuditEvent


class AuditLogger:
    """Implemente la forme attendue par application/pipeline/hooks/
    audit_hook.py::AuditSink (methode `record`, meme signature que le
    Callable[[AuditEvent], None] attendu — une instance suffit comme
    sink, sans wrapper supplementaire)."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def record(self, event: AuditEvent) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {
                "action": event.action,
                "outcome": event.outcome,
                "authorized": event.authorized,
                "detail": event.detail,
                "occurred_at": event.occurred_at.isoformat(),
            },
            ensure_ascii=False,
        )
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Ecrit chaque AuditEvent en une ligne JSON (format JSON Lines), en
#   ajout (append) au fichier d'audit — jamais de reecriture complete.
# Pourquoi dans infrastructure/logging/ (charte) :
# - Adaptateur remplacable du canal d'audit (Callable attendu par
#   application/pipeline/hooks/audit_hook.py::AuditSink), distinct du
#   logger applicatif technique (config.py/app_logger.py) : l'audit est
#   un journal METIER structure (voir plan produit, "journalise les
#   operations... audit JSON structure"), pas un log de debogage.
# Ce qu'il ne contient PAS :
# - Aucune decision de QUAND emettre un evenement (c'est
#   application/pipeline/hooks/audit_hook.py).
# - Aucune rotation de fichier ni limite de taille en V1 (coherent avec
#   le volume attendu — usage local, quelques evenements par run — un
#   besoin de rotation reel justifierait de revisiter ce choix).
# Points cles :
# - record() est directement passable comme AuditSink
#   (`audit_logger.record`) a application/pipeline/executor.py, sans
#   fonction intermediaire.
# - Format JSON Lines (un objet JSON par ligne) plutot qu'un tableau JSON
#   unique : permet l'ajout en continu sans jamais relire/reecrire le
#   fichier entier.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py cree une instance, dont la methode
#   record est injectee comme audit_sink partout ou le pipeline en a
#   besoin.
#---------------------------------------------------------------------->
