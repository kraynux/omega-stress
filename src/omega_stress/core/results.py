# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Result[T, E] generique : valeur de retour typee pour les echecs metier attendus."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Issue reussie d'une operation, porte la valeur produite."""

    value: T

    @property
    def is_ok(self) -> bool:
        return True

    @property
    def is_err(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Echec metier attendu, porte l'erreur (typiquement une DomainError).

    E est declare covariant : Ok/Err sont immuables (frozen), donc un
    Err[ValidationError] peut legitimement etre traite comme un
    Err[ValidationError | UnauthorizedTargetError] — necessaire pour que
    des commands comme application/commands/pin_target.py puissent
    retourner directement le Result d'un appel intermediaire sans le
    reenvelopper artificiellement."""

    error: E

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def is_err(self) -> bool:
        return True


Result = Ok[T] | Err[E]
"""Alias d'union utilise comme type de retour par tout command/query pouvant
echouer pour une raison metier prevue (voir ARCHITECTURE.md §5.1)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Definit le type Result[T, E] (variantes Ok/Err) utilise dans tout le
#   projet pour representer un echec metier attendu comme une valeur de
#   retour typee plutot que comme une exception Python.
# - Ok et Err sont deux dataclasses distinctes reunies par l'alias Result ;
#   isinstance(r, Ok) / isinstance(r, Err) suffit a narrower le type avec
#   mypy, aucune methode unwrap() n'est fournie pour forcer l'appelant a
#   traiter explicitement les deux branches.
# Pourquoi dans core/ (charte) :
# - C'est un concept de langage transverse a toutes les couches internes
#   (domain, application), pas un utilitaire generique sans rapport avec le
#   metier (ce qui justifierait shared/) ni une regle metier en soi.
# - Deplace depuis shared/result.py d'une version anterieure de la charte :
#   un Result est un vocabulaire transverse au meme titre que les enums et
#   les exceptions de core/, pas un simple helper (voir ARCHITECTURE.md §2,
#   description de shared/).
# Ce qu'il ne contient PAS :
# - Aucune dependance vers domain/, application/, infrastructure/.
# - Aucune logique de traduction d'exception (c'est le role des adaptateurs
#   d'infrastructure, voir ARCHITECTURE.md §5.3).
# Points cles :
# - Ok[T].value / Err[E].error portent la charge utile.
# - is_ok / is_err sont des raccourcis de lecture, pas des remplacements du
#   pattern matching / isinstance pour le narrowing de type.
# - Generique sur T et E independamment : Result[LoadPlan, DomainError] par
#   exemple.
# - T et E sont declares covariant=True : Ok/Err sont immuables, donc un
#   Ok[Duration] est valablement un Ok[Duration | X], meme logique pour
#   Err — sans cela, mypy refuse qu'un command retourne directement le
#   Result d'un appel intermediaire dont le type d'erreur est plus etroit
#   que celui declare par la signature du command appelant.
# Comment il sera utilise (apercu) :
# - Toute fonction de application/commands/ et application/queries/ pouvant
#   echouer pour une raison metier retourne Result[T, DomainError] (ou un
#   sous-type d'ApplicationError une fois traduit a la frontiere).
# - domain/load/validators.py l'utilisera pour retourner un plan valide ou
#   une ValidationError/ThresholdExceededError.
#---------------------------------------------------------------------->
