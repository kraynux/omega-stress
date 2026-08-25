# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : desepingler une cible."""
from __future__ import annotations

from omega_stress.ports.target_repository import TargetRepository


def unpin_target(target_id: str, *, target_repository: TargetRepository) -> None:
    """Desepingle une cible. Idempotent : desepingler une cible deja non
    epinglee n'est pas une erreur (voir domain/targets/service.py, qui ne
    definit volontairement pas de regle metier pour cette action)."""
    target_repository.unpin(target_id)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Appel direct au port target_repository, sans intermediaire domaine.
# Pourquoi dans application/commands/ (charte) :
# - Existe comme command distinct (plutot qu'un appel direct au
#   repository depuis interfaces/) uniquement pour garder la meme
#   convention d'acces que le reste de l'application : interfaces/
#   n'appelle jamais un port directement, toujours via application/.
# Ce qu'il ne contient PAS :
# - Aucune regle metier (voir domain/targets/service.py, qui n'a pas de
#   fonction unpin() correspondante — deliberement, voir son INFO DEV).
# - Aucune valeur de retour : desepingler ne produit rien a afficher au-
#   dela d'une confirmation implicite de succes.
# Points cles :
# - Ne verifie pas que target_id existe avant d'appeler unpin() : c'est a
#   l'implementation du port de rester silencieusement no-op sur un id
#   inconnu (coherent avec l'idempotence attendue).
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/settings_screen.py ou widgets/target_picker.py
#   (action "desepingler").
#---------------------------------------------------------------------->
