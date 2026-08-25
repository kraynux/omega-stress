# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tableau des reperes de charge (debit/connexions/durees) par type de
test et niveau, affiche dans screens/help_screen.py."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_stress.interfaces.tui.presenters.load_reference_presenter import load_reference_rows


class LoadReferenceTable(DataTable):
    """DataTable en lecture seule, une ligne par (famille de test,
    niveau) — donnees entierement figees (aucune query, aucun port),
    chargees directement au montage."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns(
            "Type de test",
            "Niveau",
            "Dimension pilotee",
            "Cible visee",
            "Simultaneite reelle",
            "Pre-check",
            "Durees disponibles",
        )
        for row in load_reference_rows():
            self.add_row(
                row.test_type,
                row.level,
                row.dimension,
                row.target,
                row.burst,
                row.precheck,
                row.durations,
            )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Rend en colonnes les valeurs de charge reelles par type de test et
#   niveau (presenters/load_reference_presenter.py), pour repondre au
#   besoin utilisateur "controler les metriques par type de tests... et
#   leur niveau, fais moi le recap sous forme de tableau".
# Pourquoi dans interfaces/tui/widgets/ (charte) :
# - Widget d'affichage pur : ne lit aucun port, aucun repository, aucun
#   DependencyContainer — seulement des donnees deja figees par le
#   presenter, meme role que history_table.py/target_table.py pour leurs
#   propres DTO.
# Ce qu'il ne contient PAS :
# - Aucune pagination/tri/filtrage : 12 lignes fixes (3 familles x 4
#   niveaux), toujours affichees en entier.
# Points cles :
# - zebra_stripes=True (2026-08-25) : lisibilite sur 12 lignes de largeur
#   variable, DataTable natif Textual (pas une convention deja etablie
#   ailleurs dans ce projet — history_table.py/target_table.py n'en ont
#   pas besoin, moins de lignes/colonnes).
# - add_columns() sans largeur explicite (comme history_table.py) :
#   chaque colonne se dimensionne sur son contenu le plus large ;
#   DataTable defile horizontalement de lui-meme si la somme depasse la
#   largeur du terminal (comportement natif Textual, aucune config
#   supplementaire necessaire).
# Comment il sera utilise :
# - screens/help_screen.py, section "Reperes de charge".
#---------------------------------------------------------------------->
