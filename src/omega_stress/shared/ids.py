# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Generation d'identifiants opaques."""
from __future__ import annotations

import uuid


def new_id() -> str:
    """Identifiant opaque unique (hex UUID4), utilise pour toute entite
    creee cote application (profil, run, job d'export...)."""
    return uuid.uuid4().hex

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de generation d'identifiants pour tout le
#   projet, afin qu'aucune couche ne reimplemente sa propre logique
#   d'ID (uuid brut, compteur, etc.) de facon divergente.
# Pourquoi dans shared/ (charte) :
# - Utilitaire transverse non metier : generer un identifiant n'est ni une
#   regle de domaine ni un detail d'infrastructure specifique.
# Ce qu'il ne contient PAS :
# - Aucune notion de format specifique a une entite (pas de prefixe
#   "profile-" ou "run-" : les identifiants restent opaques et
#   interchangeables entre types d'entites).
# Points cles :
# - Toujours appelee explicitement par l'appelant au moment de la
#   creation (jamais un default_factory cache sur une dataclass), pour
#   rester coherent avec le style "parametres explicites" deja retenu
#   pour l'horodatage dans domain/ (voir shared/clock.py).
# Comment il sera utilise (apercu) :
# - application/commands/create_profile.py et les futurs commands de
#   creation (pin_target genere son propre id cote Target en amont,
#   run_request_load pour l'id de LoadPlan/LoadRun, etc.) recoivent
#   new_id comme parametre id_factory (voir shared/typing.py::IdFactory),
#   jamais un appel en dur a uuid dans le command lui-meme — permet de
#   substituer un generateur deterministe dans les tests.
#---------------------------------------------------------------------->
