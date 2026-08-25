# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine absolue de la hierarchie d'exceptions du projet (ARCHITECTURE.md §5.2)."""
from __future__ import annotations


class OmegaStressError(Exception):
    """Racine commune a toutes les exceptions du projet, quelle que soit la
    couche. DomainError, ApplicationError, InfrastructureError, etc. en
    heritent chacune indirectement en heritant de leur propre racine de
    couche (voir domain/errors.py, application/exceptions.py, ...)."""


class CapabilityRegistryError(OmegaStressError):
    """Erreur de consolidation ou de lecture dans core/capability_registry.py
    (ex. capacite demandee jamais enregistree)."""


class ConfigurationError(OmegaStressError):
    """Configuration invalide ou incomplete detectee au demarrage
    (infrastructure/config/), avant meme que l'application ne soit prete."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Definit la racine absolue OmegaStressError et les deux exceptions
#   veritablement transverses qui ne relevent d'aucune couche metier ou
#   technique en particulier.
# Pourquoi dans core/ (charte) :
# - OmegaStressError doit pouvoir etre importee par n'importe quelle couche
#   sans creer de dependance vers l'exterieur ; core/ est la seule couche
#   dont toutes les autres dependent (directement ou indirectement).
# Ce qu'il ne contient PAS :
# - Pas DomainError (domain/errors.py), pas ApplicationError
#   (application/exceptions.py), pas InfrastructureError
#   (infrastructure/exceptions.py), pas InterfaceError (interfaces/
#   exceptions.py) : chaque couche a sa propre racine specifique, qui herite
#   in fine de OmegaStressError mais vit dans sa propre couche.
# - Aucune logique de traduction d'exception : c'est la responsabilite de
#   chaque adaptateur d'infrastructure (voir ARCHITECTURE.md §5.3).
# Points cles :
# - CapabilityRegistryError : leve par core/capability_registry.py, jamais
#   par un probe d'infrastructure (qui remonte un signal brut, pas une
#   erreur de registre).
# - ConfigurationError : reserve aux echecs de configuration au demarrage,
#   pas aux echecs metier previsibles pendant un run (qui sont des
#   DomainError portees par un Result, voir core/results.py).
# Comment il sera utilise (apercu) :
# - app/bootstrap.py peut lever ConfigurationError si un chemin var/ requis
#   est inaccessible.
# - Tous les tests unitaires de core/ peuvent asserter isinstance(exc,
#   OmegaStressError) comme garde-fou generique.
#---------------------------------------------------------------------->
