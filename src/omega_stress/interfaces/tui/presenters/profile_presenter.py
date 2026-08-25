# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : prepare les ProfileDTO pour l'affichage (tri, libelles)."""
from __future__ import annotations

from omega_stress.application.dto.profile_dto import ProfileDTO


def sorted_for_display(profiles: tuple[ProfileDTO, ...]) -> tuple[ProfileDTO, ...]:
    """Favoris d'abord, puis ordre alphabetique du nom (voir plan produit,
    ecran "Profils")."""
    return tuple(sorted(profiles, key=lambda p: (not p.favorite, p.name.lower())))


def status_label(profile: ProfileDTO) -> str:
    """Libelle humain du statut fige/modifiable d'un profil."""
    return "Fige" if profile.frozen else "Modifiable"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Met en forme les ProfileDTO deja produits par
#   application/queries/list_profiles.py : ordre d'affichage et libelles,
#   rien d'autre.
# Pourquoi dans interfaces/tui/presenters/ (charte) :
# - application/queries/list_profiles.py documente explicitement que le
#   tri d'affichage (favoris d'abord) est du ressort de ce presenter, pas
#   de la query elle-meme (qui reste un simple passe-plat du repository).
# Ce qu'il ne contient PAS :
# - Aucun appel a un port/repository : prend uniquement des ProfileDTO
#   deja recuperes en entree.
# Points cles :
# - sorted_for_display() est un tri stable pur (aucun effet de bord),
#   testable sans App.run_test() ni fixture Textual.
# Comment il sera utilise :
# - controllers/profile_controller.py, screens/profiles.py.
#---------------------------------------------------------------------->
