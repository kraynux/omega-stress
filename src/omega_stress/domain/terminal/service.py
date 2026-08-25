# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Decision du profil de rendu a partir des signaux bruts du terminal (ARCHITECTURE.md §4, §8)."""
from __future__ import annotations

from omega_stress.domain.terminal.models import TerminalProfile, TerminalSignals
from omega_stress.domain.terminal.policies import (
    DEFAULT_RENDER_PROFILE,
    TERMINAL_FAMILY_PROFILES,
    most_restrictive,
    render_profile_ceiling_for_size,
)


def resolve_render_profile(signals: TerminalSignals) -> TerminalProfile:
    """Combine la famille de terminal et sa taille : le profil retenu est
    le plus restrictif des deux (une taille insuffisante degrade meme un
    terminal par ailleurs complet, jamais l'inverse)."""
    family_profile = TERMINAL_FAMILY_PROFILES.get(signals.family, DEFAULT_RENDER_PROFILE)
    size_ceiling = render_profile_ceiling_for_size(signals.columns, signals.rows)
    resolved = most_restrictive(family_profile, size_ceiling)
    return TerminalProfile(signals=signals, render_profile=resolved)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul point de decision du profil de rendu applicable (etape 3 partielle
#   de la chaine Capacites — la decision finale, avant guard d'autorisation
#   ARCHITECTURE.md §4).
# Pourquoi dans domain/terminal/ (charte) :
# - "terminal_policy_service" au sens de ARCHITECTURE.md §2 : combine des
#   politiques pures (domain/terminal/policies.py) sans aucune I/O.
# Ce qu'il ne contient PAS :
# - Aucune lecture reelle de terminal (infrastructure/terminal/).
# - Aucune application du profil decide (c'est
#   interfaces/tui/rendering/render_profile_resolver.py, qui ne recalcule
#   jamais cette decision — voir ARCHITECTURE.md §10, anti-patterns
#   interdits).
# - Aucun avertissement utilisateur (mode manuel force un theme
#   partiellement compatible, etc.) : c'est application/commands/
#   select_render_profile.py qui orchestre l'avertissement eventuel.
# Points cles :
# - Fonction pure et deterministe : memes TerminalSignals -> meme
#   TerminalProfile, testable sans aucun mock.
# - most_restrictive() garantit qu'un terminal Ghostty (COMPLETE) affiche
#   dans un tmux 70 colonnes degrade quand meme vers REDUCED, jamais
#   l'inverse.
# Comment il sera utilise (apercu) :
# - application/queries/detect_terminal.py appelle
#   infrastructure/terminal/detector.py puis resolve_render_profile().
# - application/commands/select_render_profile.py persiste le resultat via
#   ports/settings_store.py si le mode n'est pas auto.
#---------------------------------------------------------------------->
