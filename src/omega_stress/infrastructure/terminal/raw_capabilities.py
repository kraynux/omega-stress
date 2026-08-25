# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Lecture des signaux bruts du terminal (variables d'environnement, taille)."""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RawTerminalSignals:
    """Signaux tels que remontes par le systeme, sans aucune interpretation."""

    term: str
    term_program: str
    colorterm: str
    is_ssh: bool
    columns: int
    rows: int
    has_terminator_marker: bool
    has_konsole_marker: bool
    has_gnome_terminal_marker: bool


def read_raw_signals() -> RawTerminalSignals:
    """Lit les variables d'environnement et la taille de terminal
    actuelles. Ne decide de rien : voir
    infrastructure/terminal/fallback_resolver.py pour l'interpretation.

    has_terminator_marker/has_konsole_marker/has_gnome_terminal_marker
    (2026-08-25, bug reel rapporte : le terminal reel de l'utilisateur,
    Terminator, se resolvait en famille "xterm" au lieu de "terminator")
    : TERM/TERM_PROGRAM ne suffisent PAS a identifier ces trois terminaux
    de bureau Linux courants — contrairement a Ghostty/Alacritty/WezTerm/
    Kitty, ils laissent TERM a sa valeur par defaut de compatibilite
    ("xterm-256color") et ne renseignent PAS TERM_PROGRAM (convention
    surtout suivie par les terminaux macOS/iTerm). Chacun pose en
    revanche sa propre variable d'environnement caracteristique, verifiee
    sur un Terminator reel pendant ce correctif (TERMINATOR_UUID) et
    documentee pour les deux autres (KONSOLE_VERSION, GNOME_TERMINAL_
    SCREEN) — voir fallback_resolver.py pour leur consommation."""
    columns, rows = shutil.get_terminal_size(fallback=(80, 24))
    return RawTerminalSignals(
        term=os.environ.get("TERM", ""),
        term_program=os.environ.get("TERM_PROGRAM", ""),
        colorterm=os.environ.get("COLORTERM", ""),
        is_ssh="SSH_CLIENT" in os.environ or "SSH_CONNECTION" in os.environ,
        columns=columns,
        rows=rows,
        has_terminator_marker="TERMINATOR_UUID" in os.environ,
        has_konsole_marker="KONSOLE_VERSION" in os.environ,
        has_gnome_terminal_marker=(
            "GNOME_TERMINAL_SCREEN" in os.environ or "GNOME_TERMINAL_SERVICE" in os.environ
        ),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Remonte des faits bruts sur le terminal courant : variables
#   d'environnement pertinentes et taille detectee.
# Pourquoi dans infrastructure/terminal/ (charte) :
# - Pur sondage technique (os.environ, shutil), aucune decision. Ne
#   contient et n'importe rien de la matrice terminal -> profil de rendu
#   (domain/terminal/policies.py), conformement a ARCHITECTURE.md §2.
# Ce qu'il ne contient PAS :
# - Aucune resolution de famille de terminal (voir fallback_resolver.py).
# - Aucune decision de profil de rendu (voir domain/terminal/service.py).
# Points cles :
# - shutil.get_terminal_size() a un fallback (80, 24) explicite : coherent
#   avec MINIMUM_USABLE_COLUMNS/ROWS de domain/terminal/policies.py, qui
#   sont aussi le seuil de la reduction maximale (mono).
# - is_ssh se base uniquement sur la presence des variables
#   SSH_CLIENT/SSH_CONNECTION, standard pour detecter une session SSH.
# - has_*_marker (2026-08-25) : PRESENCE uniquement (bool), jamais la
#   valeur elle-meme (ex. TERMINATOR_UUID est un UUID de session sans
#   signification hors de ce processus) — voir docstring de
#   read_raw_signals() pour le bug reel corrige.
# Comment il sera utilise (apercu) :
# - infrastructure/terminal/detector.py appelle read_raw_signals() puis
#   fallback_resolver.py::resolve_family() pour produire un
#   domain/terminal/models.py::TerminalSignals complet.
#---------------------------------------------------------------------->
