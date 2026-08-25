# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Valeurs de charge figees par niveau d'intensite (palier fixe et rampe).

Source produit : plan_omega-stress_v5.md, sections "Correspondance des
echelles d'intensite", "Test requetes", "Test connexions", "Test charge".
Les valeurs numeriques sont identiques entre l'echelle "palier fixe" et
l'echelle "montee progressive" (voir docstring de niveau module ci-dessous)
— seul le nom d'affichage change selon le mode d'execution, porte par
IntensityLevel et non duplique ici.
"""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import IntensityLevel


@dataclass(frozen=True, slots=True)
class FixedRatePreset:
    """Palier fixe : cible de debit et de simultanéité pour Test requetes /
    Test connexions a un niveau d'intensite donne."""

    level: IntensityLevel
    requests_per_minute: int
    concurrent_connections: int


FIXED_RATE_PRESETS: dict[IntensityLevel, FixedRatePreset] = {
    IntensityLevel.BAS: FixedRatePreset(IntensityLevel.BAS, 250, 25),
    IntensityLevel.MOYEN: FixedRatePreset(IntensityLevel.MOYEN, 500, 50),
    IntensityLevel.HAUT: FixedRatePreset(IntensityLevel.HAUT, 1000, 100),
    IntensityLevel.MAXIMUM: FixedRatePreset(IntensityLevel.MAXIMUM, 2000, 200),
}


@dataclass(frozen=True, slots=True)
class RampPreset:
    """Palier en montee progressive (Test charge) : rampe, plateau et
    intensite maximale pour un niveau donne. Les memes valeurs numeriques
    que FixedRatePreset au meme niveau, exprimees en cible de rampe plutot
    qu'en palier fixe."""

    level: IntensityLevel
    ramp_up_minutes: float
    plateau_minutes_min: float
    plateau_minutes_max: float
    peak_requests_per_minute: int
    peak_connections: int


RAMP_PRESETS: dict[IntensityLevel, RampPreset] = {
    IntensityLevel.BAS: RampPreset(
        IntensityLevel.BAS,
        ramp_up_minutes=1,
        plateau_minutes_min=2,
        plateau_minutes_max=2,
        peak_requests_per_minute=250,
        peak_connections=25,
    ),
    IntensityLevel.MOYEN: RampPreset(
        IntensityLevel.MOYEN,
        ramp_up_minutes=1,
        plateau_minutes_min=2,
        plateau_minutes_max=2,
        peak_requests_per_minute=500,
        peak_connections=50,
    ),
    IntensityLevel.HAUT: RampPreset(
        IntensityLevel.HAUT,
        ramp_up_minutes=2,
        plateau_minutes_min=1,
        plateau_minutes_max=3,
        peak_requests_per_minute=1000,
        peak_connections=100,
    ),
    IntensityLevel.MAXIMUM: RampPreset(
        IntensityLevel.MAXIMUM,
        ramp_up_minutes=2,
        plateau_minutes_min=1,
        plateau_minutes_max=3,
        peak_requests_per_minute=2000,
        peak_connections=200,
    ),
}


def fixed_rate_preset(level: IntensityLevel) -> FixedRatePreset:
    """Accesseur explicite (leve KeyError si le niveau n'est pas dans
    l'enum — ne devrait jamais arriver, les deux tables sont completes
    pour les 4 niveaux d'IntensityLevel)."""
    return FIXED_RATE_PRESETS[level]


def ramp_preset(level: IntensityLevel) -> RampPreset:
    return RAMP_PRESETS[level]

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte les valeurs numeriques concretes de charge (req/min, connexions,
#   rampe, plateau) pour les 4 niveaux d'IntensityLevel, dans les deux
#   representations necessaires (palier fixe et montee progressive).
# Pourquoi dans domain/load/ (charte) :
# - Politique de produit au sens de ARCHITECTURE.md §2 : ces valeurs
#   figurent telles quelles dans des tableaux de plan_omega-stress_v5.md.
#   Toute evolution des seuils doit etre appliquee ici ET dans le document
#   produit pour ne pas diverger (rappel explicite du plan : "Toute
#   evolution ulterieure des seuils doit etre appliquee aux deux echelles
#   simultanement").
# Ce qu'il ne contient PAS :
# - Les regles de gating (pre-check obligatoire, durees autorisees) : voir
#   policies.py, separe par lisibilite.
# - Aucune construction de LoadPlan ou de RampStep concrets (c'est
#   domain/load/builders.py, qui consommera ces presets comme entree).
# - Aucune validation qu'un plan respecte ces presets (domain/load/
#   validators.py).
# Points cles :
# - FIXED_RATE_PRESETS et RAMP_PRESETS portent exactement les memes valeurs
#   numeriques par niveau (250/500/1000/2000 req-min, 25/50/100/200
#   connexions) : c'est intentionnel, voir docstring de module — le plan
#   produit insiste sur le fait qu'il s'agit d'UNE SEULE echelle lue
#   differemment, pas de deux echelles independantes.
# - Les deux dict sont completes pour les 4 valeurs d'IntensityLevel a la
#   creation du fichier : fixed_rate_preset()/ramp_preset() n'ont donc pas
#   besoin de gerer un cas manquant en V1.
# Comment il sera utilise (apercu) :
# - domain/load/builders.py (ramp_builder) consommera RAMP_PRESETS pour
#   construire la sequence de RampStep d'un Test charge.
# - application/commands/run_request_load.py et run_connection_load.py
#   consommeront FIXED_RATE_PRESETS via un profil ou le mode manuel borne.
# - interfaces/tui/screens/request_panel.py (et les panneaux equivalents)
#   afficheront ces valeurs sans jamais les recalculer localement.
#---------------------------------------------------------------------->
