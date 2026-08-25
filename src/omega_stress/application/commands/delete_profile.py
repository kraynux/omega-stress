# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command : supprimer definitivement un profil."""
from __future__ import annotations

from omega_stress.ports.profile_repository import ProfileRepository


def delete_profile(profile_id: str, *, profile_repository: ProfileRepository) -> None:
    """Supprime un profil, fige ou non (voir ports/profile_repository.py::
    delete(), suppression definitive, distincte d'un archivage)."""
    profile_repository.delete(profile_id)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Appel direct au port profile_repository, sans intermediaire domaine
#   (meme patron que unpin_target.py).
# Pourquoi dans application/commands/ (charte) :
# - Existe comme command distinct uniquement pour garder la meme
#   convention d'acces que le reste de l'application : interfaces/
#   n'appelle jamais un port directement, toujours via application/.
# Ce qu'il ne contient PAS :
# - Aucune regle metier ni confirmation : la confirmation utilisateur est
#   geree cote ecran (interfaces/tui/screens/confirm.py), AVANT que ce
#   command ne soit appele.
# - Aucune verification que le profil existe avant suppression :
#   idempotent, coherent avec ports/profile_repository.py::delete()
#   (DELETE FROM ... WHERE id = ?, no-op silencieux sur un id inconnu).
# Points cles :
# - Supprime un profil FIGE aussi bien qu'un profil non fige : aucune
#   regle de domain/profiles/service.py n'interdit la suppression d'un
#   profil fige (frozen empeche seulement une modification ulterieure,
#   pas la suppression). Un run passe qui referencait ce profil_id reste
#   en historique (RunDTO.profile_id devient un id orphelin, non
#   resolvable) : screens/profiles.py avertit de cette consequence dans
#   le message de confirmation avant d'appeler ce command.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/profile_controller.py,
#   interfaces/tui/screens/profiles.py.
#---------------------------------------------------------------------->
