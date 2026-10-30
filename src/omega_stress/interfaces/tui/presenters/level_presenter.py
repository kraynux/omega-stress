# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Libelle affiche d'un niveau d'intensite (plan i18n de la suite, lot 4) : la valeur de l'enum
reste la cle enregistree et comparee, seul le libelle des listes deroulantes est traduit."""
from __future__ import annotations

from omega_stress.core.enums import IntensityLevel
from omega_stress.shared.i18n import N_, _

_LABELS: dict[IntensityLevel, str] = {
    IntensityLevel.FAIBLE: N_("faible"),
    IntensityLevel.BAS: N_("bas"),
    IntensityLevel.MOYEN: N_("moyen"),
    IntensityLevel.HAUT: N_("haut"),
    IntensityLevel.PUISSANT: N_("puissant"),
    IntensityLevel.AGRESSIF: N_("agressif"),
    IntensityLevel.VIOLENT: N_("violent"),
    IntensityLevel.MAXIMUM: N_("maximum"),
}


def level_label(level: IntensityLevel) -> str:
    return _(_LABELS.get(level, level.value))
