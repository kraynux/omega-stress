# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : resout theme et profil de rendu au demarrage du TUI."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.application.commands.select_theme import select_theme
from omega_stress.application.dto.terminal_dto import TerminalStatusDTO
from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.application.queries.detect_terminal import detect_terminal
from omega_stress.core.enums import RenderProfile
from omega_stress.domain.theme.policies import DEFAULT_TUI_THEME
from omega_stress.ports.settings_store import SettingsStore
from omega_stress.ports.terminal_detector import TerminalDetector

_THEME_KEY = "theme"


@dataclass(frozen=True, slots=True)
class StartupState:
    """Etat resolu au demarrage : terminal detecte et theme effectivement
    applique, prets avant tout montage d'ecran par app.py."""

    terminal: TerminalStatusDTO
    theme: ThemeStatusDTO


def resolve_startup_state(
    *, terminal_detector: TerminalDetector, settings_store: SettingsStore
) -> StartupState:
    """Detecte le terminal (profil de rendu automatique) puis resout le
    theme persiste (ou le theme par defaut si aucun n'a jamais ete
    choisi). Ne force jamais un profil de rendu manuel ici — voir
    render_profile_controller.py pour le forcage explicite ulterieur."""
    terminal = detect_terminal(terminal_detector=terminal_detector)
    requested_theme = settings_store.get(_THEME_KEY, DEFAULT_TUI_THEME) or DEFAULT_TUI_THEME
    theme = select_theme(
        requested_theme,
        render_profile=RenderProfile(terminal.render_profile),
        settings_store=settings_store,
    )
    return StartupState(terminal=terminal, theme=theme)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique appele par app.py juste avant App.run() : decide
#   quel theme/profil de rendu presenter des le premier ecran.
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - Orchestre deux queries/commands d'application/ (detect_terminal,
#   select_theme) sans decider lui-meme d'une regle metier.
# Ce qu'il ne contient PAS :
# - Aucune construction de Theme Textual (voir
#   rendering/textual_theme_builder.py, etape suivante dans app.py).
# Points cles :
# - Appelle select_theme() meme au demarrage (pas seulement lors d'un
#   changement explicite) : garantit que la valeur persistee reste
#   toujours un nom de theme VALIDE (repli applique et re-persiste si le
#   fichier settings.json contient un nom obsolete/corrompu).
# Comment il sera utilise :
# - interfaces/tui/app.py, avant App.run().
#---------------------------------------------------------------------->
