# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""DTO expose a la presentation pour l'etat du theme applique."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemeStatusDTO:
    """Vue plate du theme effectivement applique, avec repli eventuel."""

    theme_name: str
    render_profile: str
    fell_back_from: str | None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Forme plate de domain/theme/models.py::AppliedTheme.
# Pourquoi dans application/dto/ (charte) :
# - Objet de transfert : ni application/commands/select_theme.py ni
#   application/services/theme_selection_service.py n'exposent
#   AppliedTheme tel quel a la presentation.
# Ce qu'il ne contient PAS :
# - Aucune palette (Palette reste un detail de domain/theme/policies.py,
#   consomme directement par interfaces/tui/rendering/
#   textual_theme_builder.py, jamais transporte comme DTO — inutile pour
#   la presentation d'un simple badge ou d'un ecran de reglages, qui n'a
#   besoin que du NOM du theme actif).
# Points cles :
# - Fichier ajoute a la liste initiale de ARCHITECTURE.md §2 (qui ne
#   listait pas theme_dto.py) : ecart mineur et delibere, symetrique a
#   terminal_dto.py pour la meme raison (ne jamais exposer une entite
#   domain/ nue a la presentation) — pas une derogation a documenter en
#   §12 (ajout de fichier, pas assouplissement d'une regle).
# Comment il sera utilise (apercu) :
# - application/dto/mappers.py::applied_theme_to_dto().
# - interfaces/tui/widgets/theme_badge.py,
#   interfaces/tui/presenters/theme_presenter.py.
#---------------------------------------------------------------------->
