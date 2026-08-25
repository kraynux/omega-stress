# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Alias de type transverses reutilises dans les signatures de commands/queries."""
from __future__ import annotations

from collections.abc import Callable

IdFactory = Callable[[], str]
"""Signature d'un generateur d'identifiant injecte dans un command de
creation (voir shared/ids.py::new_id, l'implementation de production)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Regroupe les alias de type reutilises dans plusieurs signatures de
#   command/query, pour eviter de repeter des types composes (Callable[...])
#   a chaque fichier.
# Pourquoi dans shared/ (charte) :
# - Utilitaire transverse non metier, purement outillage de typage.
# Ce qu'il ne contient PAS :
# - Aucun type portant une signification metier (ces types-la vivent dans
#   domain/ ou core/enums.py) : uniquement des formes de fonctions
#   d'infrastructure legere (generation d'id, etc.).
# Points cles :
# - Volontairement tres court : n'y ajouter un alias que lorsqu'il est
#   reellement reutilise par au moins deux command/query differents (pas
#   d'alias pour une horloge injectable : voir shared/clock.py, `now` est
#   toujours passe comme valeur `datetime` explicite, pas comme callable).
# Comment il sera utilise (apercu) :
# - application/commands/create_profile.py et les futures commandes de
#   creation typent leur parametre `id_factory: IdFactory`.
#---------------------------------------------------------------------->
