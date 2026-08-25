# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Horloge de production, utilisee a la frontiere presentation/application."""
from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Heure courante en UTC. Implementation de production par defaut —
    les couches domain/application ne l'appellent jamais elles-memes,
    elles recoivent toujours `now` explicitement (voir shared/typing.py::
    IdFactory pour le meme principe applique aux identifiants)."""
    return datetime.now(timezone.utc)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Fournit l'implementation reelle de "l'heure actuelle", appelee une
#   seule fois par action utilisateur, au point d'entree (controller TUI
#   ou commande CLI), jamais a l'interieur d'un command/query ou d'un
#   objet domain.
# Pourquoi dans shared/ (charte) :
# - Utilitaire transverse non metier.
# Ce qu'il ne contient PAS :
# - Aucune notion d'horloge injectable/mockable au sens framework (pas de
#   classe Clock avec une interface a implementer) : un simple appel a
#   utc_now() au bon endroit suffit, et les tests de domain/application
#   passent directement une valeur `datetime` fixe plutot que de mocker
#   cette fonction.
# Points cles :
# - Toujours UTC (timezone-aware) : evite les ambiguites de fuseau horaire
#   dans l'historique et les exports.
# Comment il sera utilise (apercu) :
# - interfaces/tui/controllers/*.py et interfaces/cli/commands/*.py
#   appellent utc_now() une fois, puis passent le resultat en parametre
#   `now` aux commands/queries appeles.
#---------------------------------------------------------------------->
