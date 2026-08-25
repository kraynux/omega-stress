# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Validation pure de la coherence d'un LoadRun."""
from __future__ import annotations

from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.runs.models import LoadRun


def validate_run_timing(run: LoadRun) -> Result[LoadRun, ValidationError]:
    """Verifie qu'un run termine a bien une date de fin posterieure a sa
    date de depart — garde-fou de coherence, pas une regle de securite
    metier."""
    if run.finished_at is not None and run.finished_at < run.started_at:
        return Err(
            ValidationError(f"Le run {run.id} a une date de fin anterieure a sa date de depart.")
        )
    return Ok(run)


def can_be_replayed(run: LoadRun) -> bool:
    """Un run ne peut etre rejoue que s'il reference un profil fige — un
    run manuel (sans profil) ne peut pas etre relance a l'identique, faute
    de configuration reutilisable (voir plan produit, "relancer un run")."""
    return run.profile_id is not None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - validate_run_timing() : garde-fou de coherence temporelle sur un run
#   persiste ou reconstruit.
# - can_be_replayed() : predicat pur decidant si un run est eligible a la
#   relance.
# Pourquoi dans domain/runs/ (charte) :
# - Regles de coherence/eligibilite pures, distinctes des transitions
#   d'etat (domain/runs/service.py) : ce fichier ne modifie jamais un
#   LoadRun, il ne fait que le lire et repondre.
# Ce qu'il ne contient PAS :
# - Aucune transition d'etat (voir service.py).
# - Aucune reconstruction du plan a rejouer (c'est
#   application/services/run_replayer.py, qui appelle can_be_replayed()
#   avant de recharger le profil associe).
# Points cles :
# - can_be_replayed() ne verifie pas que le profil existe encore
#   reellement (suppression possible entre-temps) : seulement que le run
#   EN REFERENCE un. La verification d'existence reelle appartient a
#   application/services/run_replayer.py, qui a acces au repository.
# Comment il sera utilise (apercu) :
# - application/services/run_replayer.py appelle can_be_replayed() avant
#   de tenter une relance, et validate_run_timing() apres reconstruction
#   d'un LoadRun depuis le repository.
#---------------------------------------------------------------------->
