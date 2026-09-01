# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Calcul de l'empreinte NON invasive de la machine COURANTE (document
produit, section "Persistance et compatibilite") — voir domain/
calibration/service.py::compute_fingerprint_hash() pour deriver le nom
de fichier de calibrage persiste a partir du resultat."""
from __future__ import annotations

import os
import platform
from importlib.metadata import PackageNotFoundError, version

from omega_stress.domain.calibration.models import CalibrationFingerprint
from omega_stress.infrastructure.probe.env_reader import read_total_memory_mb
from omega_stress.infrastructure.probe.limits_reader import read_open_file_limit

_SCHEMA_VERSION = 1
_WORKERS_MODE = "asyncio-single-process"
"""Fige : Omega-Stress execute toujours le generateur comme une seule
tache asyncio in-process (ARCHITECTURE.md §5, decision de cadrage V1,
deja documentee dans infrastructure/runner/httpx_load_generator.py) —
aucun autre mode a distinguer pour l'instant."""
_SCENARIO_ID = "payload-4k"
"""Fige : un seul scenario de calibrage existe (voir domain/calibration/
policies.py::CALIBRATION_TARGET_PATH/CALIBRATION_PAYLOAD_SIZE_BYTES)."""


def compute_fingerprint() -> CalibrationFingerprint:
    """Calcule l'empreinte de la machine COURANTE — jamais d'adresse MAC
    ni de numero de serie materiel (document : "empreinte NON
    invasive"), uniquement des caracteristiques logicielles et des
    capacites mesurables deja lues ailleurs dans le projet (memes
    fonctions que infrastructure/probe/local_probe.py, jamais une
    seconde lecture divergente)."""
    open_files_soft_limit: int | None
    try:
        open_files_soft_limit = read_open_file_limit()[0]
    except OSError:
        open_files_soft_limit = None

    return CalibrationFingerprint(
        schema_version=_SCHEMA_VERSION,
        engine_version=_engine_version(),
        python_version=platform.python_version(),
        os_name=platform.system(),
        architecture=platform.machine(),
        logical_cpu_count=os.cpu_count() or 1,
        total_ram_mb=(
            float(total_mb) if (total_mb := read_total_memory_mb()) is not None else None
        ),
        open_files_soft_limit=open_files_soft_limit,
        workers_mode=_WORKERS_MODE,
        scenario_id=_SCENARIO_ID,
    )


def _engine_version() -> str:
    try:
        return version("omega-stress")
    except PackageNotFoundError:
        # Execution depuis une source non installee (ex. `pip install -e`
        # jamais lance, cas de developpement inhabituel) : jamais une
        # exception, juste une version inconnue explicite.
        return "unknown"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - compute_fingerprint() : identite logicielle/capacite de la machine
#   courante, jamais materielle.
# Pourquoi dans infrastructure/calibration/ (charte) :
# - Lecture de caracteristiques systeme concretes (platform/importlib),
#   aucune decision de domaine — CalibrationFingerprint (le type porte)
#   reste dans domain/calibration/models.py. Le HASH derive de cette
#   empreinte (domain/calibration/service.py::compute_fingerprint_hash())
#   est deliberement SEPARE de ce fichier : c'est une fonction pure sans
#   aucun appel systeme, elle vit en domain/ (voir sa propre docstring).
# Ce qu'il ne contient PAS :
# - Aucun hash/nommage de fichier (voir domain/calibration/service.py).
# - Aucune comparaison "ce calibrage est-il encore valide" (age, moteur/
#   coeurs/RAM changes) : ce fichier calcule l'empreinte COURANTE, la
#   comparaison a une empreinte PERSISTEE reste au niveau appelant
#   (application/commands/run_calibration.py ou l'ecran de consultation).
# Points cles :
# - Reutilise infrastructure/probe/env_reader.py::read_total_memory_mb()
#   et infrastructure/probe/limits_reader.py::read_open_file_limit() —
#   memes fonctions QUE local_probe.py (pre-flight), jamais une seconde
#   lecture qui pourrait diverger legerement de la premiere.
# - open_files_soft_limit/total_ram_mb restent None si non mesurables
#   (systeme non-Linux, environnement restreint) plutot que de lever :
#   un calibrage doit pouvoir se derouler (et son empreinte etre
#   persistee) meme si une seule caracteristique secondaire manque.
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py recoit compute_fingerprint
#   comme callable injecte (meme patron que shared/typing.py::IdFactory/
#   Clock — jamais importe directement, l'application ne depend jamais
#   d'infrastructure/), l'appelle une fois au debut de la progression.
#---------------------------------------------------------------------->
