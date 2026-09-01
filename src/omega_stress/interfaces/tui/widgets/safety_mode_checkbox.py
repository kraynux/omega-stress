# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Case a cocher du mode securite (garde-fous locaux CPU/memoire), active par defaut."""
from __future__ import annotations

from typing import Any

from textual.widgets import Checkbox

_LABEL = "Mode securite (protege cette machine)"


class SafetyModeCheckbox(Checkbox):
    """Wrapper autour de Checkbox portant le libelle fixe du mode
    securite, coche par defaut (contrairement a AuthorizationCheckbox,
    qui demarre non coche)."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("value", True)
        super().__init__(_LABEL, **kwargs)

# <-- INFO DEV ---------------------------------------------------------
# Role : materialise dans l'interface le choix d'activer ou non
# application/pipeline/guards/resource_guard.py (domain/load/models.py::
# LoadPlan.safety_mode) — jamais application/pipeline/guards/
# threshold_guard.py (protection de la cible testee, toujours active,
# non liee a cette case).
# Pourquoi dans interfaces/tui/widgets/ (charte) : meme role exact que
# widgets/authorization_checkbox.py (libelle fixe encapsule), seule la
# valeur par defaut differe (coche, pas decoche) — le mode securite est
# "opt-out", l'autorisation de cible est "opt-in".
# Ce qu'il ne contient PAS : aucun texte explicatif des risques (voir
# domain/load/policies.py::SAFETY_MODE_DESCRIPTION, affiche a cote par
# l'ecran appelant, jamais duplique ici) ; aucune comparaison au
# calibrage (voir presenters/calibration_presenter.py::
# envelope_comparison_message(), meme raison).
# Comment il sera utilise : screens/request_panel.py, connection_panel.py,
# ramp_panel.py.
#---------------------------------------------------------------------->
