# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Query : detecter le terminal courant et resoudre son profil de rendu."""
from __future__ import annotations

from omega_stress.application.dto.mappers import terminal_profile_to_dto
from omega_stress.application.dto.terminal_dto import TerminalStatusDTO
from omega_stress.domain.terminal.service import resolve_render_profile
from omega_stress.ports.terminal_detector import TerminalDetector


def detect_terminal(*, terminal_detector: TerminalDetector) -> TerminalStatusDTO:
    """Sonde le terminal courant (port) puis decide son profil de rendu
    (domain), sans persister quoi que ce soit — voir
    application/commands/select_render_profile.py pour la persistance
    d'un choix manuel."""
    signals = terminal_detector.detect()
    profile = resolve_render_profile(signals)
    return terminal_profile_to_dto(profile)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Query en lecture seule : combine le port terminal_detector et le
#   service domain/terminal/service.py::resolve_render_profile.
# Pourquoi dans application/queries/ (charte) :
# - Aucune modification d'etat (contrairement a
#   application/commands/select_render_profile.py, qui persiste un choix
#   via ports/settings_store.py).
# Ce qu'il ne contient PAS :
# - Aucune persistance : cette query repond juste "que verrait-on la, la
#   ou l'utilisateur est actuellement" sans rien enregistrer.
# Points cles :
# - C'est le seul point d'entree qui combine
#   ports/terminal_detector.py et domain/terminal/service.py — aucun
#   autre command/query ne doit refaire cet appel en double.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/startup_controller.py au demarrage, avant
#   toute selection manuelle de profil de rendu.
#---------------------------------------------------------------------->
