# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tableau listant l'historique des runs (application/dto/run_dto.py)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_stress.application.dto.run_dto import RunDTO


class HistoryTable(DataTable):
    """DataTable en lecture seule, une ligne par run passe."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("ID", "Cible", "Profil", "Demarre", "Verdict")

    def load_runs(self, runs: tuple[RunDTO, ...]) -> None:
        self.clear()
        for run in runs:
            self.add_row(
                run.id[:8],
                run.target_address,
                f"{run.family}/{run.level}",
                run.started_at,
                run.verdict or "en cours",
                key=run.id,
            )

# <-- INFO DEV ---------------------------------------------------------
# Role : affichage tabulaire pur des RunDTO deja recuperes par une query
# (application/queries/list_run_history.py).
# Pourquoi dans interfaces/tui/widgets/ (charte) : ne fait aucun appel a
# un port ni a un repository, se contente de rendre des DTO en lignes.
# Ce qu'il ne contient PAS : pagination/tri — geres en amont par la query
# ou par le presenter (history_presenter.py) qui prepare le tuple final.
# Points cles :
# - run.target_address (2026-08-24, non tronque : bug reel rapporte
#   alors — une adresse manuelle non epinglee, ex. "https://exemple.com/",
#   n'affichait plus que "https://" — les 8 premiers caracteres). Champ
#   lui-meme renomme le 2026-08-25 : la colonne affichait auparavant
#   run.target_id, illisible pour une cible EPINGLEE (id opaque genere,
#   ex. "657000045dbgr4100346", bug reel rapporte separement — voir
#   application/dto/run_dto.py::RunDTO.target_address pour la resolution
#   complete). add_columns() sans largeur explicite dimensionne chaque
#   colonne sur son contenu le plus large (comportement par defaut de
#   DataTable) : aucune autre configuration necessaire pour que la colonne
#   "Cible" s'elargisse avec l'adresse complete. run.id reste tronque a 8
#   caracteres (abreviation d'UUID usuelle, pas la meme plainte).
# Comment il sera utilise : screens/history.py.
#---------------------------------------------------------------------->
