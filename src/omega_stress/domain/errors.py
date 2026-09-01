# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine et vocabulaire des erreurs metier attendues (ARCHITECTURE.md §5.2)."""
from __future__ import annotations

from omega_stress.core.exceptions import OmegaStressError


class DomainError(OmegaStressError):
    """Racine de toute erreur metier attendue, portee par Result.Err
    (core/results.py), jamais levee comme une exception Python classique
    dans le flux normal d'un command/query."""


class ValidationError(DomainError):
    """Valeur ou plan mal forme (ex. duree hors des choix fermes,
    intensite non reconnue)."""


class ThresholdExceededError(DomainError):
    """Seuil de securite depasse (ex. debit reel > seuil d'arret).

    signal (Phase 2 garde-fous, raison d'arret structuree) identifie
    QUEL declencheur a leve l'erreur — "threshold_exceeded" par defaut
    (comportement historique inchange, seuil par intervalle unique),
    ou l'un des signaux de fenetre glissante/ressources generateur
    (voir domain/load/validators.py). Consomme par
    application/pipeline/abort.py pour construire un RunEvent.kind
    specifique plutot qu'un seul "threshold_exceeded" generique pour
    toute cause d'arret."""

    def __init__(self, message: str, *, signal: str = "threshold_exceeded") -> None:
        super().__init__(message)
        self.signal = signal


class UnauthorizedTargetError(DomainError):
    """Confirmation d'autorisation absente : case non cochee et cible non
    deja epinglee-autorisee (ARCHITECTURE.md §7)."""


class PrecheckRequiredError(DomainError):
    """Pre-check obligatoire non valide pour un niveau Violent/Maximum
    (domain/load/policies.py : PRECHECK_MANDATORY_LEVELS)."""


class IncompatibleTerminalError(DomainError):
    """Rendu impossible dans l'environnement detecte, sans fallback
    disponible (terminal sous la taille minimale, capacite DISQUALIFIED)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Definit DomainError (racine) et les cinq sous-types transverses a
#   plusieurs sous-domaines de domain/ (cibles, profils, load, runs,
#   terminal) — voir ARCHITECTURE.md §2 (regle de placement des erreurs) et
#   §5.2 (hierarchie complete).
# Pourquoi dans domain/ (racine, pas un sous-domaine) (charte) :
# - Ces cinq erreurs concernent le lancement d'un run dans son ensemble
#   (autorisation de cible + validation de plan + seuils + pre-check +
#   compatibilite terminal), pas un seul sous-domaine isole : les rattacher
#   arbitrairement a l'un d'eux aurait force les autres a importer ce
#   sous-domaine juste pour son type d'erreur, ce qui est le couplage
#   horizontal que ARCHITECTURE.md §0 (tableau des ecarts) cherche a eviter.
# - Chaque sous-domaine (domain/load/exceptions.py, domain/runs/
#   exceptions.py, ...) peut ajouter ses propres exceptions plus etroites,
#   heritant de DomainError, quand un besoin reellement specifique apparait
#   — aucune n'existe encore, ces fichiers restent vides jusque-la plutot
#   que peuples par anticipation.
# Ce qu'il ne contient PAS :
# - Aucune logique de validation elle-meme (c'est domain/load/validators.py,
#   domain/targets/validation.py, etc.) : ce fichier ne fait que nommer les
#   echecs possibles.
# - Aucune serialisation JSON/texte : le verdict d'un run (ARCHITECTURE.md
#   §5.2) est construit a partir de ces types par domain/reports/, pas ici.
# Points cles :
# - Toutes heritent de DomainError, qui herite de OmegaStressError
#   (core/exceptions.py) : un `except OmegaStressError` generique les
#   attrape toutes sans les nommer une a une.
# - Sont sans etat autre que le message standard d'Exception : pas
#   d'attribut structure supplementaire en V1 (ex. pas de champ "seuil
#   depasse : valeur X"), a enrichir seulement si un besoin reel de
#   presentation le demande.
# Comment il sera utilise (apercu) :
# - application/pipeline/guards/*.py leve ou retourne (via Result.Err) ces
#   types depuis chaque guard correspondant.
# - domain/load/validators.py, domain/targets/service.py les utilisent
#   directement.
#---------------------------------------------------------------------->
