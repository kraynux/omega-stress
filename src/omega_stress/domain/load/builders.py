# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Construction des etapes de rampe (Test charge) a partir des presets figes."""
from __future__ import annotations

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.models import RampStep
from omega_stress.domain.load.presets import ramp_preset


def build_ramp_steps(level: IntensityLevel, *, duration_minutes: int) -> tuple[RampStep, ...]:
    """Construit la sequence ramp-up + plateau pour un niveau donne, mise
    a l'echelle de `duration_minutes` (la duree REELLEMENT choisie pour ce
    test, voir Duration.for_level()).

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

    Mise a l'echelle (2026-09-01, bug reel rapporte : "1 min" choisi sur
    Maximum, ramp_up_minutes=4 du preset ignore le choix de duree,
    n'explorait donc que le premier quart de la montee, debit moyen
    observe tres faible) : ramp_up et plateau sont recalcules
    PROPORTIONNELLEMENT pour que leur somme corresponde exactement a
    duration_minutes, jamais aux valeurs figees du preset telles quelles.
    """
    preset = ramp_preset(level)
    preset_total = preset.ramp_up_minutes + preset.plateau_minutes_min
    scale = duration_minutes / preset_total if preset_total > 0 else 1.0
    return (
        RampStep(
            order=1,
            duration_minutes=preset.ramp_up_minutes * scale,
            start_ratio=0.0,
            end_ratio=1.0,
        ),
        RampStep(
            order=2,
            duration_minutes=preset.plateau_minutes_min * scale,
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
# - duration_minutes obligatoire, sans defaut (2026-09-01, bug reel
#   rapporte avec captures d'ecran) : avant ce correctif, ramp_up_minutes/
#   plateau_minutes_min du preset (fixes par NIVEAU, ex. 4 min de montee
#   pour Maximum) etaient utilises tels quels, totalement independants de
#   la duree REELLEMENT choisie par l'utilisateur dans le formulaire (ex.
#   1 min) — deux notions de duree jamais reconciliees (voir application/
#   commands/run_ramp_load.py, INFO DEV, "duree TOTALE bornee... deux
#   notions de duree paralleles"). Un test de 1 min sur Maximum n'explorait
#   donc que le premier quart (1/4 min) de la montee vers le pic, jamais le
#   plateau, d'ou un debit moyen observe tres faible (~240 req/min au lieu
#   d'un pic vise a 20000). scale = duration_minutes / (ramp_up_minutes +
#   plateau_minutes_min du preset) : preserve les PROPORTIONS relatives du
#   preset (ex. 80% montee / 20% plateau pour Maximum) tout en garantissant
#   que la somme des deux etapes correspond exactement a la duree choisie,
#   que celle-ci soit plus courte OU plus longue que le total du preset.
# Comment il sera utilise (apercu) :
# - application/commands/run_ramp_load.py appelle build_ramp_steps(level,
#   duration_minutes=...) avec la duree DEJA validee (Duration.for_level())
#   pour assembler le LoadPlan avant validation.
#---------------------------------------------------------------------->
