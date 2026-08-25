# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : vider les cibles recentes (non epinglees)."""
from __future__ import annotations

from omega_stress.ports.target_repository import TargetRepository


def clear_recent_targets(*, target_repository: TargetRepository) -> None:
    """Efface les cibles recentes. Les cibles epinglees ne sont jamais
    touchees (voir ports/target_repository.py::clear_recent())."""
    target_repository.clear_recent()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Appel direct au port target_repository, sans intermediaire domaine
#   (meme patron que unpin_target.py).
# Pourquoi dans application/commands/ (charte) :
# - Existe comme command distinct uniquement pour garder la meme
#   convention d'acces que le reste de l'application : interfaces/
#   n'appelle jamais un port directement, toujours via application/.
# Ce qu'il ne contient PAS :
# - Aucune regle metier ni confirmation : la confirmation utilisateur est
#   geree cote ecran (interfaces/tui/screens/confirm.py), AVANT que ce
#   command ne soit appele — ce fichier execute, il ne demande jamais.
# Points cles :
# - Distinct de clear_all_targets.py : celui-ci ne touche jamais les
#   cibles epinglees (autorisation deliberee, pas un historique passif).
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/load_controller.py,
#   interfaces/tui/screens/settings_screen.py.
#---------------------------------------------------------------------->
