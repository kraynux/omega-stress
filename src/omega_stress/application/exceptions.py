# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Hierarchie d'exceptions applicatives (ARCHITECTURE.md §5.2)."""
from __future__ import annotations

from omega_stress.core.exceptions import OmegaStressError


class ApplicationError(OmegaStressError):
    """Racine des echecs techniques inattendus survenant dans
    application/ (bug, contrat viole) — jamais utilisee pour un echec
    metier attendu, qui reste porte par un Result[T, DomainError]."""


class UseCaseExecutionError(ApplicationError):
    """Un command ou query n'a pas pu aller a son terme pour une raison
    technique non anticipee par le metier."""


class CapabilityUnavailableError(ApplicationError):
    """Une capacite requise (application/pipeline/guards/
    capability_guard.py) est MISSING ou DISQUALIFIED au moment de la
    verification."""


class PermissionDeniedError(ApplicationError):
    """Traduction applicative d'un refus d'autorisation, une fois le
    UnauthorizedTargetError du domaine remonte et contextualise."""


class PartialExecutionError(ApplicationError):
    """Une action composee (ex. plusieurs etapes de pipeline) a partiellement
    reussi avant d'echouer — l'appelant doit connaitre ce qui a deja ete
    fait pour decider d'une compensation."""


class AbortError(ApplicationError):
    """Arret volontaire d'un run en cours d'execution suite a un
    ThresholdExceededError du domaine (voir application/pipeline/abort.py)
    — renomme depuis le "RollbackError" du gabarit omega-fire, qui ne
    correspond pas au modele d'un run de charge (voir ARCHITECTURE.md §0)."""


class RunnerFailureError(ApplicationError):
    """Echec technique du generateur de charge, non qualifiable de
    depassement de seuil (ex. DNS injoignable des le depart, refus de
    connexion systematique) — traduit par l'adaptateur infrastructure
    (infrastructure/runner/httpx_load_generator.py) depuis une exception
    httpx brute, puis catche explicitement par
    application/pipeline/executor.py pour produire un verdict FAILED.
    Definie ici plutot que dans infrastructure/exceptions.py : c'est le
    seul type d'exception technique qu'application/ a legitimement besoin
    de connaitre par son nom (pour le catcher), la Dependency Rule
    interdisant a application/ d'importer infrastructure/ (voir
    ARCHITECTURE.md §5.3, qui la qualifie deja d'"erreur applicative
    generique")."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Racine ApplicationError et ses six sous-types (dont RunnerFailureError,
#   deplacee ici depuis infrastructure/exceptions.py apres detection d'une
#   violation reelle de la Dependency Rule par import-linter — voir son
#   propre docstring pour la justification complete).
# Pourquoi dans application/ (charte) :
# - Ce sont des exceptions de couche application, distinctes des
#   DomainError (domain/errors.py) : une DomainError est un echec metier
#   attendu porte par un Result, ces types-ci ne sont leves que pour un
#   echec technique reellement inattendu au niveau de l'orchestration.
# Ce qu'il ne contient PAS :
# - Aucune DomainError redefinie ici : un command/query qui recoit un
#   Result.Err(DomainError) le propage tel quel a l'appelant (interfaces/),
#   il ne le convertit pas systematiquement en ApplicationError.
# - Aucune traduction d'exception technique (sqlite3.Error, httpx.*) : ce
#   travail est fait par l'adaptateur d'infrastructure concerne AVANT que
#   l'exception n'atteigne application/ (ARCHITECTURE.md §5.3), jamais ici.
# Points cles :
# - PermissionDeniedError et CapabilityUnavailableError sont des
#   traductions applicatives, utilisees quand un guard du pipeline doit
#   remonter un refus au-dela du Result de premier niveau (ex. dans un
#   contexte ou lever est plus adapte que retourner, comme un cas
#   reellement inattendu de guard en echec technique plutot que de refus
#   metier normal).
# - AbortError est le seul renommage explicite par rapport au gabarit
#   omega-fire (RollbackError) — voir ARCHITECTURE.md §0 pour la
#   justification complete.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py, guards/*.py et hooks/*.py.
#---------------------------------------------------------------------->
