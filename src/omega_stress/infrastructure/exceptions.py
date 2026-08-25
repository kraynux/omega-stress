# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Hierarchie d'exceptions d'infrastructure (ARCHITECTURE.md §5.2, §5.3)."""
from __future__ import annotations

from omega_stress.core.exceptions import OmegaStressError


class InfrastructureError(OmegaStressError):
    """Racine des erreurs techniques d'infrastructure. Toute exception
    specifique a une technologie (sqlite3.Error, httpx.*, erreurs de
    parsing...) est traduite vers un sous-type de celle-ci par
    l'adaptateur concerne, avant de franchir la frontiere du port —
    jamais l'exception technique brute (ARCHITECTURE.md §5.3)."""


class StorageError(InfrastructureError):
    """Erreur de persistance, traduite depuis sqlite3.Error ou une erreur
    d'ecriture de fichier."""


class ParseError(InfrastructureError):
    """Erreur d'interpretation d'une donnee externe (reponse HTTP mal
    formee, fichier de configuration invalide...)."""


class AdapterConfigurationError(InfrastructureError):
    """Configuration d'un adaptateur invalide ou incomplete au demarrage
    (chemin manquant, valeur hors domaine attendu)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Racine InfrastructureError et trois sous-types, correspondant a la
#   ligne "infrastructure/exceptions.py" du tableau ARCHITECTURE.md §5.2 —
#   a l'exception de RunnerFailureError, qui vit desormais dans
#   application/exceptions.py (voir Points cles).
# Pourquoi dans infrastructure/ (charte) :
# - Ce sont les SEULES exceptions qu'un adaptateur d'infrastructure a le
#   droit de laisser franchir un port : jamais une exception specifique a
#   une bibliotheque tierce (sqlite3.Error, httpx.ConnectError...).
# Ce qu'il ne contient PAS :
# - Aucune DomainError (domain/errors.py) : un adaptateur peut choisir de
#   traduire une exception technique en DomainError plutot qu'en
#   InfrastructureError quand le cas releve d'un critere d'arret metier
#   (ex. timeout httpx pendant un run -> ThresholdExceededError, voir
#   ports/load_runner.py) — les deux chemins de traduction coexistent
#   selon le contexte, ce fichier ne couvre que le second (echec
#   reellement technique, pas un critere d'arret).
# - RunnerFailureError : deplacee vers application/exceptions.py apres
#   qu'import-linter a signale une violation reelle de la Dependency Rule
#   (application/pipeline/executor.py doit catcher ce type par son nom
#   pour produire un verdict FAILED, ce qu'il ne peut pas faire si le
#   type vit dans infrastructure/, qu'application/ n'a pas le droit
#   d'importer). Les trois types restants ici ne sont jamais catches
#   nommement par application/ : ils se contentent de remonter jusqu'au
#   filet de securite de presentation (ARCHITECTURE.md §5.4) sans
#   qu'aucune couche intermediaire n'ait besoin de connaitre leur type
#   precis.
# Points cles :
# - StorageError, ParseError, AdapterConfigurationError seront leves par
#   les adaptateurs concrets une fois construits (infrastructure/storage/,
#   infrastructure/config/) — aucun n'est encore consomme ailleurs dans le
#   code a ce stade.
# Comment il sera utilise (apercu) :
# - infrastructure/storage/sqlite/*.py catchent sqlite3.Error et levent
#   StorageError.
# - infrastructure/config/loader.py peut lever AdapterConfigurationError
#   si un chemin requis est manquant au demarrage.
#---------------------------------------------------------------------->
