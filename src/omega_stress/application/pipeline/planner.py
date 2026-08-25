# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Etape 4/5 du pipeline : dernier point de validation structurelle avant execution."""
from __future__ import annotations

from omega_stress.core.results import Result
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.load.validators import PlanValidationError, validate_plan


def prepare_plan(plan: LoadPlan) -> Result[LoadPlan, PlanValidationError]:
    """Point de passage oblige avant application/pipeline/executor.py,
    quelle que soit la source du plan (domain/profiles/service.py::
    to_load_plan() pour un lancement depuis un profil fige, ou construit
    directement par un command run_*_load en mode manuel borne)."""
    return validate_plan(plan)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Etape nommee du pipeline (ARCHITECTURE.md §4) qui delegue
#   integralement a domain/load/validators.py::validate_plan().
# Pourquoi dans application/pipeline/ (charte) :
# - Existe comme etape distincte du pipeline (plutot qu'un appel direct a
#   validate_plan() depuis chaque command run_*_load) pour garder une
#   sequence d'etapes explicite et uniforme, observable et testable
#   independamment — coherent avec le decoupage guards/planner/executor
#   d'omega-fire repris par cette charte (ARCHITECTURE.md §0).
# Ce qu'il ne contient PAS :
# - Aucune construction de LoadPlan (deja fait en amont, par
#   domain/profiles/service.py::to_load_plan() ou directement par le
#   command appelant) : ce fichier ne fait que VALIDER un plan deja
#   assemble, il ne l'assemble jamais lui-meme.
# - Aucune verification d'autorisation/pre-check/capacite : deja couvertes
#   par les guards executes AVANT cette etape (authorization_guard,
#   precheck_guard, capability_guard) — validate_plan() re-verifie
#   authorisation/pre-check/duree en defense en profondeur, mais ce guard
#   pipeline reste la premiere ligne de refus rapide.
# Points cles :
# - Fonction intentionnellement mince (un seul appel) : la valeur de ce
#   fichier est de nommer explicitement l'etape dans le pipeline, pas
#   d'ajouter de la logique.
# Comment il sera utilise (apercu) :
# - Les commands run_request_load.py, run_connection_load.py,
#   run_ramp_load.py (a construire) appellent prepare_plan() juste avant
#   application/pipeline/executor.py::execute().
#---------------------------------------------------------------------->
