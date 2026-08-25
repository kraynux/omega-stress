# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tableau listant les cibles epinglees et recentes (application/dto/target_dto.py)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_stress.application.dto.target_dto import TargetDTO


class TargetTable(DataTable):
    """DataTable en lecture seule, une ligne par cible (epinglee ou
    recente) — meme convention que widgets/profile_list.py."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Adresse", "Tags", "Statut", "Derniere utilisation")

    def load_targets(self, targets: tuple[TargetDTO, ...]) -> None:
        self.clear()
        for target in targets:
            status = "epinglee" if target.pinned else "recente"
            self.add_row(
                target.base_url,
                ", ".join(target.tags) or "—",
                status,
                target.last_used_at or "—",
                key=target.id,
            )

# <-- INFO DEV ---------------------------------------------------------
# Role : affichage tabulaire pur des TargetDTO recuperes par une query
# (application/queries/list_targets.py, via interfaces/tui/controllers/
# load_controller.py::load_targets()).
# Pourquoi dans interfaces/tui/widgets/ (charte) : aucun appel port/repo,
# rendu seul — meme role que widgets/profile_list.py, widgets/
# history_table.py.
# Ce qu'il ne contient PAS : aucune action d'epinglage/desepinglage
# (geree par screens/targets.py) ; ce widget ne fait qu'afficher l'etat
# deja decide.
# Comment il sera utilise : screens/targets.py.
#---------------------------------------------------------------------->
