# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Bandeau texte OMEGA-STRESS (3 lignes, sans cadre) affiche en haut de
screens/home.py — demande explicite (2026-08-25, voir finalisation.txt) :
remplace l'ancienne composition complete (widgets/home_hero.py, deplacee
vers l'ecran de demarrage, voir widgets/splash_hero.py)."""
from __future__ import annotations

from textual import events
from textual.widgets import Static

from omega_stress.core.enums import RenderProfile

_FONT_TOKEN = "$foreground"

_WORDMARK_LINES = (
    "┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐   ┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐",
    "│║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═ └╩═══╦┐    ║    │╠══╦╩┘ ├╬══    └╩═══╦┐ └╩═══╦┐",
    "└╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘   └╩═══╩┘    ╩    └╩  ╚═┘ └╩═══╩┘ └╩═══╩┘ └╩═══╩┘",
)
"""Fourni tel quel par l'utilisateur (finalisation.txt) : OMEGA-STRESS en
un seul bandeau de lettres, sans cadre ni accroche — extrait
caractere pour caractere (pas de retranscription manuelle), voir
widgets/splash_hero.py pour la meme methode d'extraction."""

_WIDTH = max(len(line) for line in _WORDMARK_LINES)
_MIN_TERMINAL_WIDTH = _WIDTH + 6


def _build_markup() -> tuple[str, ...]:
    """Meme helper de formatage que le reste de l'application (demande :
    "avec les memes helpers de formatage par themes, ligne de texte du
    milieu en clair") : seule la ligne du MILIEU (le corps des lettres)
    passe en $foreground, hauts/bas restent "vif" ($accent par defaut du
    widget, non marque) — identique a la regle deja appliquee au cadre
    OMEGA-STRESS de widgets/splash_hero.py."""
    lines = list(_WORDMARK_LINES)
    lines[1] = f"[{_FONT_TOKEN}]{lines[1]}[/]"
    return tuple(lines)


_ART_MARKUP = _build_markup()


class HomeWordmark(Static):
    """Bandeau decoratif centre en haut de screens/home.py."""

    def __init__(self, *, render_profile: RenderProfile) -> None:
        super().__init__("\n".join(_ART_MARKUP), classes="omega-home-wordmark")
        self._render_profile = render_profile

    def set_render_profile(self, render_profile: RenderProfile) -> None:
        self._render_profile = render_profile
        self._update_visibility()

    def on_mount(self) -> None:
        self._update_visibility()

    def on_resize(self, event: events.Resize) -> None:
        self._update_visibility()

    def _update_visibility(self) -> None:
        simplified = self._render_profile is RenderProfile.MONO
        too_narrow = self.app.size.width < _MIN_TERMINAL_WIDTH
        self.display = not (simplified or too_narrow)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Bandeau OMEGA-STRESS purement decoratif, en tete de l'ecran d'accueil.
# Pourquoi dans interfaces/tui/widgets/ (charte) :
# - Widget de presentation pure, meme convention que splash_hero.py.
# Ce qu'il ne contient PAS :
# - Aucun cadre, aucune accroche, aucune silhouette : uniquement les
#   lettres OMEGA-STRESS, fournies telles quelles par l'utilisateur.
# Points cles :
# - render_profile fourni par l'appelant (screens/home.py), meme
#   convention que l'ancien widgets/home_hero.py (set_render_profile()
#   rappelable depuis on_screen_resume() si le reglage change ailleurs).
# Comment il sera utilise :
# - screens/home.py, centre horizontalement en tete d'ecran.
#---------------------------------------------------------------------->
