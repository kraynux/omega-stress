# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entite Profil : configuration de test reutilisable et figeable."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.models import Duration, Thresholds


@dataclass(frozen=True, slots=True)
class Profile:
    """Profil de test, reutilisable et historisable (voir plan produit,
    section "Profils figes"). Le champ `frozen` porte l'etat produit "figé"
    (immutabilite au sens metier : plus modifiable, seulement dupliquable),
    distinct de l'immuabilite Python de la dataclass elle-meme qui
    s'applique dans les deux cas (fige ou non)."""

    id: str
    name: str
    description: str
    default_target_id: str
    family: TestFamily
    level: IntensityLevel
    duration: Duration
    thresholds: Thresholds
    created_at: datetime
    tags: tuple[str, ...] = ()
    extended_duration_authorized: bool = False
    frozen: bool = False
    frozen_at: datetime | None = None
    favorite: bool = False
    archived: bool = False

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Entite Profil telle que decrite dans plan_omega-stress_v5.md ("Profils
#   figes") : nom, description, cible par defaut, type de test, intensite,
#   duree, seuils, tags, statut fige, favoris.
# Pourquoi dans domain/profiles/ (charte) :
# - Entite metier pure, reutilise Duration et Thresholds de domain/load/
#   (meme couche domain, reference de value object legitime entre
#   sous-domaines — voir ARCHITECTURE.md §2, note sur domain/errors.py
#   pour la meme logique appliquee aux exceptions).
# Ce qu'il ne contient PAS :
# - Aucun champ "ramp_steps" propre : pour un profil de famille RAMP, les
#   etapes de rampe sont derivees du niveau via
#   domain/load/builders.py::build_ramp_steps() au moment de convertir le
#   profil en LoadPlan (domain/profiles/service.py::to_load_plan), pas
#   stockees ici — evite une duplication de source de verite avec
#   domain/load/presets.py.
# - Aucune logique de gel/duplication (voir domain/profiles/service.py).
# - Aucune validation (voir domain/profiles/validation.py).
# Points cles :
# - extended_duration_authorized : champ explicite distinct de `frozen`.
#   Un profil peut etre fige SANS autoriser la duree etendue (5 min en
#   Haut/Maximum) — les deux notions sont independantes dans le plan
#   produit ("5 minutes seulement si le profil OU le pre-check l'autorise"
#   : c'est une autorisation specifique, pas une consequence automatique du
#   gel).
# - archived : correspond a l'action produit "archiver" un profil fige
#   (liste des actions possibles sur un profil fige, plan produit).
# Comment il sera utilise (apercu) :
# - domain/profiles/service.py::freeze()/duplicate()/to_load_plan().
# - application/dto/profile_dto.py exposera une version aplatie vers la
#   presentation.
#---------------------------------------------------------------------->
