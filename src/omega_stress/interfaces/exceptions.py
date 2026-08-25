# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Hierarchie d'exceptions de presentation, partagee par tui/ et cli/ (ARCHITECTURE.md §5.2)."""
from __future__ import annotations

from omega_stress.core.exceptions import OmegaStressError


class InterfaceError(OmegaStressError):
    """Racine des echecs propres a la couche de presentation (TUI et
    CLI), distincte des DomainError/ApplicationError qu'elle affiche."""


class UserInputError(InterfaceError):
    """Saisie utilisateur invalide avant meme d'atteindre un command/query
    (ex. argument CLI mal forme, valeur hors du vocabulaire attendu)."""


class RenderError(InterfaceError):
    """Echec de mise en forme d'un resultat deja obtenu (rare : les DTO
    sont deja des formes simples, ce type couvre surtout un gabarit ou un
    widget qui echoue a s'afficher)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Racine InterfaceError et ses deux sous-types, correspondant a la
#   ligne "interfaces/exceptions.py" du tableau ARCHITECTURE.md §5.2.
# Pourquoi dans interfaces/ (racine, pas cli/ ni tui/) (charte) :
# - Partagee par les deux adaptateurs de presentation a parite stricte
#   (ARCHITECTURE.md §2, "Deux adaptateurs... aucune regle metier ne doit
#   exister dans l'un sans exister, de la meme facon, dans l'autre") :
#   vivre a la racine de interfaces/ evite que cli/ et tui/ definissent
#   chacun leur propre variante divergente.
# Ce qu'il ne contient PAS :
# - Aucune DomainError/ApplicationError redefinie ici : ce fichier ne
#   couvre que les echecs PROPRES a la presentation elle-meme.
# Points cles :
# - UserInputError est levee AVANT tout appel a application/ (ex.
#   argparse rejette un argument), jamais apres — un echec metier
#   pendant l'execution d'un command reste une DomainError/
#   ApplicationError, jamais reconvertie en UserInputError.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py : point d'arret unique cote CLI
#   (ARCHITECTURE.md §5.4).
# - interfaces/tui/app.py aura le meme role cote TUI, une fois construit.
#---------------------------------------------------------------------->
