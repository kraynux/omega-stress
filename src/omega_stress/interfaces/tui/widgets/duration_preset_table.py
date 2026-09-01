# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tableau des profils de duree nommes D1-D6 (mode "profil"), affiche
dans screens/help_screen.py."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_stress.interfaces.tui.presenters.load_reference_presenter import (
    duration_preset_reference_rows,
)


class DurationPresetTable(DataTable):
    """DataTable en lecture seule, une ligne par profil D1-D6 — donnees
    entierement figees (aucune query, aucun port), chargees directement
    au montage. Voir widgets/load_reference_table.py, meme role et meme
    patron pour le tableau des niveaux (mode manuel)."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns(
            "ID",
            "Nom",
            "Duree totale",
            "Familles compatibles",
            "Niveaux libres",
            "Niveau renforce",
        )
        for row in duration_preset_reference_rows():
            self.add_row(
                row.id,
                row.name,
                f"{row.total_minutes} min",
                row.families,
                row.free_levels,
                row.reinforced_level,
            )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Rend en colonnes les 6 profils de duree D1-D6 (presenters/
#   load_reference_presenter.py::duration_preset_reference_rows()), pour
#   que le mode "profil" (nouveau, 2026-09-01) soit decouvrable depuis
#   l'Aide au meme titre que le mode manuel (load_reference_table.py).
# Pourquoi dans interfaces/tui/widgets/ (charte) :
# - Widget d'affichage pur, meme role que load_reference_table.py : ne
#   lit aucun port, aucun repository, aucun DependencyContainer.
# Ce qu'il ne contient PAS :
# - Aucune valeur numerique en dur : tout vient du presenter, qui lit
#   lui-meme domain/load/duration_presets.py.
# Points cles :
# - "Niveau renforce" affiche "—" quand le profil n'en propose aucun
#   (D1/D2/D3) plutot qu'une cellule vide : coherent avec le principe
#   d'un tableau de reference, jamais une case ambigue entre "aucune
#   valeur" et "valeur pas encore chargee".
# Comment il sera utilise :
# - screens/help_screen.py, section "Profils de duree D1-D6".
#---------------------------------------------------------------------->
