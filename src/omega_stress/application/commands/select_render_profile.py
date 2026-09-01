# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : choisir (ou forcer) le profil de rendu et le persister."""
from __future__ import annotations

from omega_lib.terminal.models import RenderProfile, TerminalProfile
from omega_lib.terminal.service import resolve_render_profile

from omega_stress.application.dto.mappers import terminal_profile_to_dto
from omega_stress.application.dto.terminal_dto import TerminalStatusDTO
from omega_stress.ports.settings_store import SettingsStore
from omega_stress.ports.terminal_detector import TerminalDetector

_SETTINGS_KEY = "render_profile"


def select_render_profile(
    *,
    terminal_detector: TerminalDetector,
    settings_store: SettingsStore,
    manual_override: RenderProfile | None = None,
) -> TerminalStatusDTO:
    """Determine le profil de rendu (automatique, ou force par
    manual_override en mode manuel — voir plan produit, "Reglages : ...
    mode auto") et persiste le choix retenu."""
    signals = terminal_detector.detect()
    auto_resolved = resolve_render_profile(signals)

    final_profile = manual_override if manual_override is not None else auto_resolved.render_profile
    result = TerminalProfile(signals=signals, render_profile=final_profile)

    settings_store.set(_SETTINGS_KEY, final_profile.value)
    return terminal_profile_to_dto(result)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Applique et persiste le profil de rendu, automatique ou force
#   manuellement.
# Pourquoi dans application/commands/ (charte) :
# - Orchestre ports/terminal_detector.py, domain/terminal/service.py et
#   ports/settings_store.py, sans redecider lui-meme du profil (en mode
#   automatique) : la decision reste entierement dans
#   domain/terminal/service.py::resolve_render_profile().
# Ce qu'il ne contient PAS :
# - Aucun avertissement utilisateur formate (ex. "rendu possiblement
#   partiel" si un profil force est incoherent avec la taille reelle) :
#   la decision d'afficher un avertissement reste a
#   interfaces/tui/controllers/render_profile_controller.py, qui peut
#   comparer manual_override a auto_resolved lui-meme si besoin.
# Points cles :
# - manual_override, quand fourni, N'EST PAS revalide contre la taille
#   reelle du terminal ici : le mode manuel du plan produit assume
#   explicitement un rendu possiblement degrade en cas de forçage, la
#   responsabilite de l'avertissement etant cote presentation (§8,
#   politique de theme/rendu).
# - _SETTINGS_KEY = "render_profile" est la seule definition de cette cle
#   dans le projet.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/render_profile_controller.py,
#   interfaces/tui/screens/settings_screen.py.
#---------------------------------------------------------------------->
