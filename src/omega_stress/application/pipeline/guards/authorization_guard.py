# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Guard 1/4 du pipeline : autorisation de la cible (ARCHITECTURE.md §4, §7)."""
from __future__ import annotations

from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import UnauthorizedTargetError
from omega_stress.ports.target_repository import TargetRepository


def check_authorization(
    target_id: str, *, target_repository: TargetRepository, explicit_confirmation: bool
) -> Result[None, UnauthorizedTargetError]:
    """Autorise si la cible est deja epinglee (donc deja confirmee au
    moment de l'epinglage, voir domain/targets/service.py::pin), ou si
    une confirmation explicite est fournie pour ce run precis."""
    if target_repository.get_pinned(target_id) is not None:
        return Ok(None)
    if explicit_confirmation:
        return Ok(None)
    return Err(
        UnauthorizedTargetError(
            f"Cible {target_id!r} non autorisee : ni epinglee, ni confirmation "
            f"explicite fournie pour ce run."
        )
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Premiere etape obligatoire du pipeline (ARCHITECTURE.md §4) : verifie
#   qu'un run peut demarrer sur la cible visee, avant toute construction
#   de plan.
# Pourquoi dans application/pipeline/guards/ (charte) :
# - Necessite le port target_repository (I/O) pour verifier l'epinglage :
#   ne peut pas vivre en domain/, qui n'a acces a aucun repository.
# Ce qu'il ne contient PAS :
# - Aucune decision de PERSISTANCE de l'autorisation (c'est
#   domain/targets/service.py::pin(), appele par
#   application/commands/pin_target.py — un autre chemin, en amont).
# - Aucune reimplementation de la regle : ce guard ne fait que consulter
#   l'etat deja decide (epinglage persiste, ou confirmation explicite du
#   run courant), il ne redecide jamais lui-meme des conditions
#   d'autorisation.
# Points cles :
# - Deux chemins d'autorisation valides, tous deux suffisants : cible deja
#   epinglee-autorisee (persistant, reutilisable a chaque run futur), ou
#   confirmation explicite ponctuelle pour CE run (ephemere, ne persiste
#   rien — voir application/commands/pin_target.py si l'utilisateur veut
#   la rendre persistante).
# - Retourne un Result plutot que de lever : ce refus est un echec metier
#   attendu du parcours utilisateur normal (case non cochee), pas un bug.
# Comment il sera utilise (apercu) :
# - application/pipeline/planner.py (ou les commands run_*_load) appelle
#   ce guard avant de construire le LoadPlan.
#---------------------------------------------------------------------->
