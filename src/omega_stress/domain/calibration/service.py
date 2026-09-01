# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Fonctions de service pures du sous-domaine calibration — sans I/O."""
from __future__ import annotations

import hashlib
from dataclasses import asdict

from omega_stress.domain.calibration.models import CalibrationFingerprint


def compute_fingerprint_hash(fingerprint: CalibrationFingerprint) -> str:
    """Hash stable et court derive de l'empreinte, utilise comme nom de
    fichier persiste (var/calibrations/<hash>.json) — deux appels sur la
    MEME empreinte produisent le meme hash (fonction pure, aucun etat
    externe). Le CALCUL de l'empreinte elle-meme (lecture reelle de
    platform/psutil) reste dans infrastructure/calibration/
    fingerprint.py::compute_fingerprint() — seule cette derniere touche
    le systeme, ce fichier ne fait que hacher un CalibrationFingerprint
    deja construit."""
    raw = "|".join(str(v) for v in asdict(fingerprint).values())
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - compute_fingerprint_hash() : derive un identifiant de fichier stable
#   a partir d'une empreinte machine deja construite.
# Pourquoi dans domain/calibration/ (charte) :
# - Fonction PURE (hashlib + dataclasses.asdict, aucun appel systeme) :
#   contrairement a infrastructure/calibration/fingerprint.py::
#   compute_fingerprint() (qui lit reellement platform/psutil/env_reader),
#   celle-ci ne fait que transformer une donnee deja en memoire — aucune
#   raison de la placer en infrastructure/, coherent avec domain/runs/
#   service.py (aggregate_samples()/finish(), memes fonctions pures a
#   cote des entites de son sous-domaine).
# Ce qu'il ne contient PAS :
# - Aucune lecture systeme reelle (voir infrastructure/calibration/
#   fingerprint.py::compute_fingerprint(), le seul endroit qui construit
#   un CalibrationFingerprint depuis l'etat reel de la machine).
# Points cles :
# - sha256 tronque a 16 caracteres hex : suffisant pour un nom de fichier
#   stable et lisible sur un poste local mono-utilisateur, jamais un
#   identifiant cryptographique a proprement parler.
# Comment il sera utilise (apercu) :
# - infrastructure/storage/files/json_calibration_store.py::save() nomme
#   le fichier persiste avec ce hash.
# - application/commands/run_calibration.py l'appelle pour retrouver un
#   calibrage deja persiste (CalibrationRepository.load()).
#---------------------------------------------------------------------->
