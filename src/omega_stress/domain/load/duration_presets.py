# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Profils de duree nommes D1-D6 (mode "profil"), distincts du mode manuel
de domain/load/policies.py::allowed_durations_minutes() — les deux
coexistent, jamais cumules sur un meme LoadPlan (voir domain/load/
validators.py::evaluate_duration_preset()).

Source produit : omega-stress-calibrage-profils-securite.md, sections
"Durees verrouillees" (table "Politique proposee") et "Repartition
interne d'une duree"."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import DurationPresetId, IntensityLevel, TestFamily
from omega_stress.domain.load.models import RampStep

_ALL_FAMILIES: frozenset[TestFamily] = frozenset(
    {TestFamily.REQUEST, TestFamily.CONNECTION, TestFamily.RAMP}
)


@dataclass(frozen=True, slots=True)
class DurationSplit:
    """Decoupage interne d'un profil de duree en 4 phases fixes
    (warm-up/rampe/plateau/retour au calme), en secondes — consomme par
    build_duration_preset_ramp_steps() pour produire une sequence de
    RampStep. La somme des 4 champs vaut toujours DurationPreset.
    total_minutes * 60 (verifie par les tests, pas par __post_init__ ici :
    ce sont des valeurs figees du document, pas une saisie utilisateur)."""

    warmup_seconds: int
    ramp_seconds: int
    plateau_seconds: int
    cooldown_seconds: int


@dataclass(frozen=True, slots=True)
class DurationPreset:
    """Un profil de duree nomme : duree totale fixe, decoupage interne,
    familles de test compatibles, et plage de niveaux autorises.

    free_max_level : niveau le plus haut accessible SANS confirmation
    renforcee.
    reinforced_level : UN niveau de plus, accessible SEULEMENT avec la
    confirmation renforcee (domain/load/policies.py::
    REINFORCED_CONFIRMATION_PHRASE) — None si aucun niveau supplementaire
    n'est propose meme avec confirmation (D1/D2 : deja Maximum sans
    condition ; D3 : Maximum simplement absent, pas de palier renforce).
    Tout niveau au-dela de reinforced_level (ou de free_max_level si
    reinforced_level est None) n'est jamais propose a cette duree."""

    id: DurationPresetId
    name: str
    total_minutes: int
    split: DurationSplit
    compatible_families: frozenset[TestFamily]
    free_max_level: IntensityLevel
    reinforced_level: IntensityLevel | None


DURATION_PRESETS: dict[DurationPresetId, DurationPreset] = {
    DurationPresetId.D1: DurationPreset(
        id=DurationPresetId.D1,
        name="quick",
        total_minutes=1,
        split=DurationSplit(
            warmup_seconds=5, ramp_seconds=10, plateau_seconds=40, cooldown_seconds=5
        ),
        compatible_families=_ALL_FAMILIES,
        free_max_level=IntensityLevel.MAXIMUM,
        reinforced_level=None,
    ),
    DurationPresetId.D2: DurationPreset(
        id=DurationPresetId.D2,
        name="short",
        total_minutes=5,
        split=DurationSplit(
            warmup_seconds=15, ramp_seconds=30, plateau_seconds=240, cooldown_seconds=15
        ),
        compatible_families=_ALL_FAMILIES,
        free_max_level=IntensityLevel.MAXIMUM,
        reinforced_level=None,
    ),
    DurationPresetId.D3: DurationPreset(
        id=DurationPresetId.D3,
        name="standard",
        total_minutes=15,
        split=DurationSplit(
            warmup_seconds=30, ramp_seconds=90, plateau_seconds=750, cooldown_seconds=30
        ),
        compatible_families=_ALL_FAMILIES,
        free_max_level=IntensityLevel.VIOLENT,
        reinforced_level=None,
    ),
    DurationPresetId.D4: DurationPreset(
        id=DurationPresetId.D4,
        name="resilience",
        total_minutes=30,
        split=DurationSplit(
            warmup_seconds=60, ramp_seconds=180, plateau_seconds=1500, cooldown_seconds=60
        ),
        compatible_families=_ALL_FAMILIES,
        free_max_level=IntensityLevel.AGRESSIF,
        reinforced_level=IntensityLevel.VIOLENT,
    ),
    DurationPresetId.D5: DurationPreset(
        id=DurationPresetId.D5,
        name="extended",
        total_minutes=60,
        split=DurationSplit(
            warmup_seconds=120, ramp_seconds=300, plateau_seconds=3060, cooldown_seconds=120
        ),
        compatible_families=_ALL_FAMILIES,
        free_max_level=IntensityLevel.PUISSANT,
        reinforced_level=IntensityLevel.AGRESSIF,
    ),
    DurationPresetId.D6: DurationPreset(
        id=DurationPresetId.D6,
        name="soak",
        total_minutes=120,
        split=DurationSplit(
            warmup_seconds=180, ramp_seconds=600, plateau_seconds=6240, cooldown_seconds=180
        ),
        compatible_families=frozenset({TestFamily.CONNECTION, TestFamily.RAMP}),
        free_max_level=IntensityLevel.HAUT,
        reinforced_level=IntensityLevel.PUISSANT,
    ),
}


def duration_preset(preset_id: DurationPresetId) -> DurationPreset:
    """Accesseur explicite (leve KeyError si l'id n'est pas dans l'enum —
    ne devrait jamais arriver, DURATION_PRESETS est complet pour les 6
    valeurs de DurationPresetId)."""
    return DURATION_PRESETS[preset_id]


def build_duration_preset_ramp_steps(preset: DurationPreset) -> tuple[RampStep, ...]:
    """Traduit le decoupage interne d'un profil en 4 RampStep — meme
    mecanisme d'interpolation que builders.py::build_ramp_steps() (via
    infrastructure/runner/engine_params.py::_ramp_ratio_at(), aucune
    nouvelle logique d'interpolation) : warm-up (ratio 0.0->0.0, pas de
    charge), rampe (0.0->1.0 lineaire), plateau (1.0->1.0), retour au
    calme (1.0->0.0 lineaire)."""
    split = preset.split
    return (
        RampStep(
            order=1,
            duration_minutes=split.warmup_seconds / 60,
            start_ratio=0.0,
            end_ratio=0.0,
        ),
        RampStep(
            order=2,
            duration_minutes=split.ramp_seconds / 60,
            start_ratio=0.0,
            end_ratio=1.0,
        ),
        RampStep(
            order=3,
            duration_minutes=split.plateau_seconds / 60,
            start_ratio=1.0,
            end_ratio=1.0,
        ),
        RampStep(
            order=4,
            duration_minutes=split.cooldown_seconds / 60,
            start_ratio=1.0,
            end_ratio=0.0,
        ),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte les 6 profils de duree nommes D1-D6 (duree totale fixe,
#   decoupage interne, familles compatibles, plage de niveaux) et traduit
#   un profil en sequence de RampStep exploitable par le runner.
# Pourquoi dans domain/load/ (charte) :
# - Meme sous-domaine que presets.py/policies.py : ce sont des valeurs de
#   politique produit figees dans omega-stress-calibrage-profils-
#   securite.md, pas une valeur calculee dynamiquement.
# Ce qu'il ne contient PAS :
# - Aucune validation de plan (verifier qu'un niveau est autorise pour un
#   profil donne, verifier la confirmation renforcee) : voir domain/load/
#   validators.py::evaluate_duration_preset(), qui consomme ce module
#   plutot que de dupliquer ses donnees.
# - Aucune valeur de charge (req/min, connexions) : reste dans presets.py,
#   resolue au moment de l'execution a partir du ratio produit ici.
# Points cles :
# - RampStep importe directement de domain/load/models.py (aucun cycle :
#   models.py ne connait pas duration_presets.py, sens unique).
# - Warm-up a ratio CONSTANT 0.0 (jamais une petite charge positive) :
#   interpretation retenue en l'absence de precision du document sur la
#   cible exacte du warm-up — periode d'observation avant charge, pas une
#   charge reduite. A revoir explicitement si une valeur differente est
#   tranchee plus tard.
# - D6 (soak) exclut TestFamily.REQUEST de compatible_families (document :
#   colonne "Types compatibles" ne mentionne que "Charge, connexions") —
#   un test de requetes est borne en VOLUME, pas en duree soutenue, jamais
#   pertinent sur un profil de 120 min axe sur la derive.
# - Les 6 DurationSplit somment exactement a total_minutes*60 (verifie par
#   tests/unit/domain/load/test_duration_presets.py, pas par une
#   validation runtime ici — valeurs figees du document, jamais une
#   saisie utilisateur).
# Comment il sera utilise (apercu) :
# - domain/load/validators.py::evaluate_duration_preset() consomme
#   free_max_level/reinforced_level/compatible_families.
# - application/commands/run_*_load.py (mode profil) appelleront
#   build_duration_preset_ramp_steps() pour peupler LoadPlan.ramp_steps
#   quand duration_preset_id est fourni.
#---------------------------------------------------------------------->
