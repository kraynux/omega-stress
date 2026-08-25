# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : vider l'historique des runs."""
from __future__ import annotations

from omega_stress.ports.run_repository import RunRepository


def clear_run_history(*, run_repository: RunRepository) -> None:
    """Efface tout l'historique des runs (voir ports/run_repository.py::
    clear())."""
    run_repository.clear()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Appel direct au port run_repository, sans intermediaire domaine (meme
#   patron que unpin_target.py).
# Pourquoi dans application/commands/ (charte) :
# - Existe comme command distinct uniquement pour garder la meme
#   convention d'acces que le reste de l'application : interfaces/
#   n'appelle jamais un port directement, toujours via application/.
# Ce qu'il ne contient PAS :
# - Aucune regle metier ni confirmation : la confirmation utilisateur est
#   geree cote ecran (interfaces/tui/screens/confirm.py), AVANT que ce
#   command ne soit appele.
# Points cles :
# - Purge complete, sans filtre (coherent avec ports/run_repository.py::
#   clear(), aucun parametre) : une purge partielle n'a pas ete demandee.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/history_controller.py,
#   interfaces/tui/screens/settings_screen.py.
#---------------------------------------------------------------------->
