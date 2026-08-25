# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Resolution du nom de famille de terminal a partir des signaux bruts."""
from __future__ import annotations

from omega_stress.infrastructure.terminal.raw_capabilities import RawTerminalSignals

_KNOWN_FAMILIES: tuple[str, ...] = (
    "ghostty",
    "alacritty",
    "wezterm",
    "kitty",
    "konsole",
    "terminator",
    "xfce4-terminal",
)
"""Familles reconnues directement par correspondance de sous-chaine dans
TERM/TERM_PROGRAM — doit rester coherent avec les cles de
domain/terminal/policies.py::TERMINAL_FAMILY_PROFILES."""


def resolve_family(signals: RawTerminalSignals) -> str:
    """Traduit des signaux bruts en un nom de famille normalise, cle
    attendue par domain/terminal/policies.py::TERMINAL_FAMILY_PROFILES.
    Un nom non reconnu par cette table se voit appliquer
    DEFAULT_RENDER_PROFILE cote domaine — cette fonction ne leve jamais
    d'erreur pour une famille inconnue."""
    term = signals.term.lower()
    term_program = signals.term_program.lower()

    if signals.is_ssh:
        modern = signals.colorterm.lower() in ("truecolor", "24bit") or "256" in term
        return "ssh-modern" if modern else "ssh-legacy"

    if signals.has_terminator_marker:
        return "terminator"
    if signals.has_konsole_marker:
        return "konsole"
    if signals.has_gnome_terminal_marker:
        return "gnome-terminal"

    for family in _KNOWN_FAMILIES:
        if family in term or family in term_program:
            return family

    if "gnome" in term or "gnome" in term_program:
        return "gnome-terminal"
    if "rxvt" in term:
        return "urxvt"
    if term == "linux":
        return "linux-tty"
    if "xterm" in term:
        return "xterm"

    return term or "unknown"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit RawTerminalSignals en un nom de famille normalise (chaine),
#   sans jamais decider du profil de rendu associe.
# Pourquoi dans infrastructure/terminal/ (charte) :
# - Heuristique technique de reconnaissance de terminal (pattern matching
#   sur des variables d'environnement), pas une regle metier : la table
#   qui associe une famille a un profil de rendu reste entierement dans
#   domain/terminal/policies.py.
# Ce qu'il ne contient PAS :
# - Aucune reference a RenderProfile ni a domain/terminal/ : ce fichier
#   ignore totalement ce que domain/ fera du nom qu'il produit.
# Points cles :
# - Les noms retournes doivent rester synchronises avec les cles de
#   domain/terminal/policies.py::TERMINAL_FAMILY_PROFILES — une famille
#   non presente dans cette table se degrade silencieusement vers
#   DEFAULT_RENDER_PROFILE cote domaine, jamais une erreur ici.
# - SSH est priorise avant toute autre correspondance : une session SSH
#   modifie fondamentalement les capacites reelles, independamment du
#   terminal local de l'utilisateur.
# - has_terminator_marker/has_konsole_marker/has_gnome_terminal_marker
#   (2026-08-25, bug reel rapporte et reproduit : sur un Terminator reel,
#   TERM="xterm-256color" et TERM_PROGRAM="" — resolus AVANT ce correctif
#   en famille "xterm" via le dernier repli ci-dessous, jamais
#   "terminator", donc RenderProfile.REDUCED applique au lieu de STANDARD
#   sur TOUTE session Terminator reelle). Verifies avant la boucle
#   _KNOWN_FAMILIES (qui ne peut de toute facon jamais les matcher, TERM/
#   TERM_PROGRAM ne contenant pas ces noms sur ces terminaux) : Terminator,
#   Konsole et GNOME Terminal renseignent chacun leur propre variable
#   d'environnement caracteristique la ou TERM/TERM_PROGRAM ne le font
#   pas — voir raw_capabilities.py::read_raw_signals() pour le detail par
#   variable. xfce4-terminal reste une limite connue non couverte (aucune
#   variable d'environnement caracteristique documentee a ce jour) : se
#   degrade vers le repli "xterm" existant, pas une regression introduite
#   par ce correctif.
# Comment il sera utilise (apercu) :
# - infrastructure/terminal/detector.py.
#---------------------------------------------------------------------->
