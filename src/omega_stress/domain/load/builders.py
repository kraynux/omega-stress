# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Construction des etapes de rampe (Test charge) a partir des presets figes."""
from __future__ import annotations

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.models import RampStep
from omega_stress.domain.load.presets import ramp_preset


def build_ramp_steps(level: IntensityLevel) -> tuple[RampStep, ...]:
    """Construit la sequence ramp-up + plateau pour un niveau donne.

    Interpretation retenue pour la duree de plateau : les presets
    expriment un intervalle (plateau_minutes_min a plateau_minutes_max,
    ex. "1 a 3 min" pour Haut/Maximum) plutot qu'une valeur unique. En
    l'absence d'un mecanisme de choix fin documente dans le plan produit,
    cette fonction retient systematiquement la borne basse
    (plateau_minutes_min) comme valeur par defaut prudente, coherente avec
    la philosophie generale de bornage du produit ("choix fermes, pas de
    saisie libre totale"). Une duree de plateau differente dans cet
    intervalle resterait possible via un profil fige explicite, a
    construire alors avec des RampStep distincts plutot qu'en modifiant
    cette fonction.
    """
    preset = ramp_preset(level)
    return (
        RampStep(order=1, duration_minutes=preset.ramp_up_minutes, start_ratio=0.0, end_ratio=1.0),
        RampStep(
            order=2,
            duration_minutes=preset.plateau_minutes_min,
            start_ratio=1.0,
            end_ratio=1.0,
        ),
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit un RampPreset (domain/load/presets.py) en sequence concrete de
#   RampStep (domain/load/models.py) : une etape de montee (0 -> pic) puis
#   une etape de plateau (pic maintenu).
# Pourquoi dans domain/load/ (charte) :
# - Logique metier pure de construction, sans I/O, consommant uniquement
#   d'autres modules du meme sous-domaine.
# Ce qu'il ne contient PAS :
# - Aucune valeur numerique en dur (tout vient de presets.py).
# - Aucune validation de plan complet (voir validators.py).
# - Aucune resolution de la valeur absolue (req/min ou connexions) a
#   chaque instant du run : ce sera le role du runner d'infrastructure au
#   moment de l'execution, a partir du ratio et du RampPreset.
# Points cles :
# - Retourne toujours exactement 2 etapes en V1 (pas de cooldown : le plan
#   produit le mentionne comme "eventuel" sans donner de valeurs
#   concretes, donc non implemente plutot qu'invente).
# - Le choix de plateau_minutes_min plutot que plateau_minutes_max est une
#   interpretation documentee ci-dessus, pas une valeur du plan produit :
#   a revoir explicitement si un mecanisme de choix dans l'intervalle est
#   precise plus tard.
# Comment il sera utilise (apercu) :
# - application/commands/run_ramp_load.py appellera build_ramp_steps() pour
#   assembler le LoadPlan avant validation.
#---------------------------------------------------------------------->
