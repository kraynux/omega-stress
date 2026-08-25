# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation concrete du port TerminalDetector."""
from __future__ import annotations

from omega_stress.domain.terminal.models import TerminalSignals
from omega_stress.infrastructure.terminal.fallback_resolver import resolve_family
from omega_stress.infrastructure.terminal.raw_capabilities import read_raw_signals


class SystemTerminalDetector:
    """Implemente ports/terminal_detector.py::TerminalDetector. Nommee
    SystemTerminalDetector (pas TerminalDetector) pour ne pas porter le
    meme nom que le Protocol qu'elle implemente (charte §3)."""

    def detect(self) -> TerminalSignals:
        raw = read_raw_signals()
        return TerminalSignals(
            family=resolve_family(raw),
            columns=raw.columns,
            rows=raw.rows,
            is_ssh=raw.is_ssh,
        )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Assemble raw_capabilities.py et fallback_resolver.py en un
#   domain/terminal/models.py::TerminalSignals complet, seul point
#   d'entree du port terminal_detector.py.
# Pourquoi dans infrastructure/terminal/ (charte) :
# - Adaptateur remplacable : orchestre deux sous-modules techniques sans
#   ajouter de logique propre.
# Ce qu'il ne contient PAS :
# - Aucune decision de profil de rendu (c'est
#   domain/terminal/service.py::resolve_render_profile, appele par
#   l'application juste apres avoir recu ce TerminalSignals).
# Points cles :
# - Classe volontairement fine : detect() est une simple composition,
#   toute la logique reelle vit dans les deux fichiers qu'elle assemble.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py injecte une instance unique dans
#   application/queries/detect_terminal.py via le port.
#---------------------------------------------------------------------->
