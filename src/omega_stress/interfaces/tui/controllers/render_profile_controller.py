# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Controller : applique et persiste le profil de rendu (auto ou force)."""
from __future__ import annotations

from omega_stress.application.commands.select_render_profile import select_render_profile
from omega_stress.application.dto.terminal_dto import TerminalStatusDTO
from omega_stress.core.enums import RenderProfile
from omega_stress.ports.settings_store import SettingsStore
from omega_stress.ports.terminal_detector import TerminalDetector


def apply_render_profile(
    *,
    terminal_detector: TerminalDetector,
    settings_store: SettingsStore,
    manual_override: RenderProfile | None = None,
) -> TerminalStatusDTO:
    """Applique le profil de rendu automatique, ou force manual_override
    si fourni explicitement (ecran Reglages, mode manuel)."""
    return select_render_profile(
        terminal_detector=terminal_detector,
        settings_store=settings_store,
        manual_override=manual_override,
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de screens/settings_screen.py vers
#   application/commands/select_render_profile.py.
# Pourquoi dans interfaces/tui/controllers/ (charte) :
# - Fine couche d'appel direct, sans logique propre : la decision
#   automatique reste entierement dans domain/terminal/service.py.
# Ce qu'il ne contient PAS :
# - Aucun avertissement formate en cas de forçage incoherent avec la
#   taille reelle du terminal (deja documente comme responsabilite de
#   l'appelant dans application/commands/select_render_profile.py) :
#   c'est a screens/settings_screen.py de comparer manual_override au
#   TerminalStatusDTO precedent si un avertissement est necessaire.
# Comment il sera utilise :
# - screens/settings_screen.py (mode auto/manuel).
#---------------------------------------------------------------------->
