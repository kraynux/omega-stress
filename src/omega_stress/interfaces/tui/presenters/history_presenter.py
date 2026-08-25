# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : prepare l'historique des runs pour l'affichage tabulaire."""
from __future__ import annotations

from omega_stress.application.dto.run_dto import RunDTO


def most_recent_first(runs: tuple[RunDTO, ...]) -> tuple[RunDTO, ...]:
    """Trie explicitement par date de demarrage decroissante : ne suppose
    aucun ordre de la part de application/queries/list_history.py (qui
    ne garantit pas d'ordre precis, voir son INFO DEV)."""
    return tuple(sorted(runs, key=lambda r: r.started_at, reverse=True))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Ordonne les RunDTO pour l'ecran "Historique" (les plus recents en
#   premier), seule mise en forme necessaire a ce niveau (le detail par
#   ligne est deja pret via run_presenter.py::verdict_label()).
# Pourquoi dans interfaces/tui/presenters/ (charte) :
# - Le tri est un choix de presentation, pas une garantie de
#   application/queries/list_history.py (qui reste un passe-plat du
#   repository, potentiellement deja trie ou non selon l'implementation
#   du port).
# Ce qu'il ne contient PAS :
# - Aucun filtre (cible/profil/limite) : deja geres par les parametres de
#   list_history() elle-meme, ce presenter ne fait que trier le resultat
#   recu.
# Points cles :
# - started_at est une chaine ISO 8601 (RunDTO) : le tri lexicographique
#   est equivalent au tri chronologique pour ce format, sans parsing.
# Comment il sera utilise :
# - controllers/history_controller.py avant transmission a
#   widgets/history_table.py::load_runs().
#---------------------------------------------------------------------->
