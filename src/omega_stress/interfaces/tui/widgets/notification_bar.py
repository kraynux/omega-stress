# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Bandeau de notifications transitoires (arret auto, goulot detecte...)."""
from __future__ import annotations

from textual.widgets import Static


class NotificationBar(Static):
    """Widget-sink : appelable directement comme NotificationSink applicatif."""

    def __call__(self, message: str) -> None:
        self.update(message)
        self.remove_class("-hidden")

    def clear_message(self) -> None:
        self.update("")
        self.add_class("-hidden")

# <-- INFO DEV ---------------------------------------------------------
# Role : rend visible les notifications publiees par
# application/pipeline/hooks/notification_hook.py (type NotificationSink
# = Callable[[str], None]).
# Pourquoi dans interfaces/tui/widgets/ (charte) : l'instance elle-meme
# EST le sink (via __call__), evite un adaptateur intermediaire inutile —
# c'est le controller qui l'injecte dans le hook au demarrage du run.
# Ce qu'il ne contient PAS : aucune file/historique de messages — chaque
# nouvel appel remplace le precedent (bandeau, pas journal).
# Comment il sera utilise : controllers/load_controller.py (injection du
# hook), screens/request_panel.py et consorts (affichage).
#---------------------------------------------------------------------->
