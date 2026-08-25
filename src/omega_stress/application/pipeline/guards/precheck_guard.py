# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Guard 2/4 du pipeline : pre-check obligatoire pour Haut/Maximum (ARCHITECTURE.md §4)."""
from __future__ import annotations

from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import PrecheckRequiredError
from omega_stress.domain.load.policies import is_precheck_mandatory


def check_precheck(
    level: IntensityLevel, *, precheck_validated: bool
) -> Result[None, PrecheckRequiredError]:
    """Refuse le demarrage si le niveau exige un pre-check
    (domain/load/policies.py::is_precheck_mandatory) et qu'aucun pre-check
    valide n'a ete fourni pour ce run."""
    if is_precheck_mandatory(level) and not precheck_validated:
        return Err(
            PrecheckRequiredError(
                f"Le niveau {level.value} exige un pre-check automatique valide "
                f"avant de demarrer."
            )
        )
    return Ok(None)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Deuxieme etape obligatoire du pipeline : verifie qu'un pre-check
#   valide couvre le niveau demande, avant toute construction de plan.
# Pourquoi dans application/pipeline/guards/ (charte) :
# - Delegue integralement la regle a domain/load/policies.py ; ce guard
#   n'ajoute aucune logique metier, il sert de point d'arret precoce du
#   pipeline (fail fast avant de construire un plan complet).
# Ce qu'il ne contient PAS :
# - Aucun calcul de validite temporelle du pre-check (comparaison a
#   PRECHECK_VALIDITY_HOURS) : precheck_validated est deja un booleen
#   tranche par l'appelant (typiquement application/commands/
#   run_precheck.py ou la lecture d'un profil fige avec pre-check recent),
#   pas recalcule ici.
# - Aucune execution de pre-check reel (c'est
#   application/commands/run_precheck.py, un command distinct qui produit
#   la valeur precheck_validated consommee ici).
# Points cles :
# - Duplique volontairement une partie de ce que
#   domain/load/validators.py::validate_plan() verifie deja (defense en
#   profondeur : rejeter tot, avant de construire un LoadPlan complet,
#   plutot que de decouvrir le meme refus plus tard) — les deux restent
#   coherents car les deux appellent la meme fonction
#   is_precheck_mandatory() de domain/load/policies.py.
# Comment il sera utilise (apercu) :
# - application/pipeline/planner.py (ou les commands run_*_load) appelle
#   ce guard juste apres authorization_guard.
#---------------------------------------------------------------------->
