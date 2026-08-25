# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : effacer toutes les cibles (recentes ET epinglees)."""
from __future__ import annotations

from omega_stress.ports.target_repository import TargetRepository


def clear_all_targets(*, target_repository: TargetRepository) -> None:
    """Efface toutes les cibles, y compris les epinglees (reperd les
    autorisations deja accordees, voir ports/target_repository.py::
    clear_all())."""
    target_repository.clear_all()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Appel direct au port target_repository, sans intermediaire domaine
#   (meme patron que unpin_target.py/clear_recent_targets.py).
# Pourquoi dans application/commands/ (charte) :
# - Existe comme command distinct uniquement pour garder la meme
#   convention d'acces que le reste de l'application : interfaces/
#   n'appelle jamais un port directement, toujours via application/.
# Ce qu'il ne contient PAS :
# - Aucune regle metier ni confirmation : la confirmation utilisateur est
#   geree cote ecran (interfaces/tui/screens/confirm.py, avec un message
#   plus severe que pour clear_recent_targets.py — cette action reperd
#   des autorisations), AVANT que ce command ne soit appele.
# Points cles :
# - Distinct de clear_recent_targets.py : celui-ci efface aussi les
#   cibles epinglees, action plus destructrice (perte d'autorisations
#   deja accordees, a recommencer).
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/load_controller.py,
#   interfaces/tui/screens/settings_screen.py.
#---------------------------------------------------------------------->
