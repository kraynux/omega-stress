# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Forme generique d'un evenement d'audit, independante du support de journalisation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Trace d'une action passee par le pipeline (ARCHITECTURE.md §4),
    consommee par application/pipeline/hooks/audit_hook.py."""

    action: str
    outcome: str
    authorized: bool
    detail: str = ""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Definit la forme neutre d'un evenement d'audit (quoi, quand, autorise
#   par qui/quoi, issue), sans presumer de son format de stockage.
# Pourquoi dans core/ (charte) :
# - Vocabulaire transverse consomme a la fois par application/pipeline/
#   hooks/audit_hook.py (qui le construit) et infrastructure/logging/
#   audit_logger.py (qui le serialise) : ni l'un ni l'autre ne doit imposer
#   sa forme de donnee a l'autre.
# Ce qu'il ne contient PAS :
# - Aucune ecriture disque, aucun format JSON/texte concret (c'est
#   infrastructure/logging/audit_logger.py).
# - Aucune decision sur QUAND emettre un evenement (c'est
#   application/pipeline/hooks/audit_hook.py).
# Points cles :
# - occurred_at par defaut = maintenant en UTC (voir aussi shared/clock.py
#   si une horloge injectable est necessaire pour les tests plus tard).
# - authorized : bool explicite, distinct de outcome (une action peut etre
#   autorisee et quand meme echouer techniquement).
# Comment il sera utilise (apercu) :
# - application/pipeline/hooks/audit_hook.py construit un AuditEvent a
#   chaque etape significative du pipeline (lancement, arret automatique,
#   export).
# - infrastructure/logging/audit_logger.py l'ecrit en JSON structure dans
#   var/.
#---------------------------------------------------------------------->
