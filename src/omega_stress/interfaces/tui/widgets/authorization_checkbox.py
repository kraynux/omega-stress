# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Case de confirmation d'autorisation, obligatoire avant tout run."""
from __future__ import annotations

from typing import Any

from textual.widgets import Checkbox

_LABEL = "Je confirme etre autorise a tester cette cible"


class AuthorizationCheckbox(Checkbox):
    """Wrapper autour de Checkbox portant le libelle d'autorisation fixe."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(_LABEL, **kwargs)

# <-- INFO DEV ---------------------------------------------------------
# Role : materialise dans l'interface la confirmation exigee par la
# politique d'autorisation (domain/target/policies.py, guard
# application/pipeline/guards/authorization_guard.py).
# Pourquoi dans interfaces/tui/widgets/ (charte) : ne decide rien — coche
# non validee => le guard applicatif refusera le lancement de toute
# facon ; cette case n'est qu'une ergonomie, pas un controle de securite.
# Ce qu'il ne contient PAS : aucune verification que la cible est deja
# epinglee-autorisee (ce cas dispense l'utilisateur de la case, gere par
# le controller qui decide de l'afficher ou non).
# Comment il sera utilise : screens/request_panel.py, connection_panel.py,
# ramp_panel.py.
#---------------------------------------------------------------------->
