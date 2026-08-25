# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tableau listant les profils enregistres (application/dto/profile_dto.py)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_stress.application.dto.profile_dto import ProfileDTO


class ProfileList(DataTable):
    """DataTable en lecture seule, une ligne par profil."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Nom", "Type", "Statut", "Duree")

    def load_profiles(self, profiles: tuple[ProfileDTO, ...]) -> None:
        self.clear()
        for profile in profiles:
            status = "fige" if profile.frozen else "modifiable"
            self.add_row(
                profile.name,
                f"{profile.family}/{profile.level}",
                status,
                f"{profile.duration_minutes} min",
                key=profile.id,
            )

# <-- INFO DEV ---------------------------------------------------------
# Role : affichage tabulaire pur des ProfileDTO recuperes par une query
# (application/queries/list_profiles.py).
# Pourquoi dans interfaces/tui/widgets/ (charte) : aucun appel port/repo,
# rendu seul.
# Ce qu'il ne contient PAS : creation/edition de profil — geree par
# screens/profile_wizard.py et application/commands/create_profile.py.
# Comment il sera utilise : screens/profiles.py.
#---------------------------------------------------------------------->
