# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de detection des signaux bruts du terminal."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.terminal.models import TerminalSignals


class TerminalDetector(Protocol):
    """Port consomme par application/queries/detect_terminal.py,
    implemente par infrastructure/terminal/detector.py."""

    def detect(self) -> TerminalSignals: ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de detection des signaux bruts du terminal courant.
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (obtenir des TerminalSignals), jamais
#   par la source technique (os.environ, ioctl de taille de terminal,
#   etc.) qui reste privee a l'implementation.
# Ce qu'il ne contient PAS :
# - Aucune decision de profil de rendu (c'est
#   domain/terminal/service.py::resolve_render_profile, appele APRES ce
#   port par l'application).
# - Aucune implementation concrete (voir
#   infrastructure/terminal/detector.py et raw_capabilities.py).
# Points cles :
# - Une seule methode, sans parametre : le contexte d'execution (variables
#   d'environnement, sortie standard) est implicite a l'implementation,
#   pas passe en argument.
# Comment il sera utilise (apercu) :
# - application/queries/detect_terminal.py appelle detect() puis
#   domain/terminal/service.py::resolve_render_profile().
#---------------------------------------------------------------------->
