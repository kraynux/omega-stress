# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Erreurs specifiques au sous-domaine calibration (voir domain/errors.py
pour les erreurs transverses a plusieurs sous-domaines)."""
from __future__ import annotations

from omega_stress.domain.errors import DomainError


class CalibrationPreconditionError(DomainError):
    """Une precondition de calibrage n'est pas satisfaite (machine deja
    sous forte pression, calibrage/test deja actif) — voir domain/
    calibration/validators.py::evaluate_preconditions() et
    policies.py pour les seuils exacts. Le calibrage est refuse ou
    reporte, jamais tente sur une machine deja chargee (resultat
    inutilisable ou artificiellement faible, voir document produit)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Erreur specifique au sous-domaine calibration, trop etroite pour
#   vivre dans domain/errors.py (voir sa propre docstring : "chaque
#   sous-domaine peut ajouter ses propres exceptions... quand un besoin
#   reellement specifique apparait").
# Pourquoi dans domain/calibration/ (charte) :
# - Meme convention que domain/load/exceptions.py (fichier prevu par
#   domain/errors.py mais reste vide jusqu'a un besoin reel) : ce
#   sous-domaine a desormais ce besoin.
# Comment il sera utilise (apercu) :
# - domain/calibration/validators.py::evaluate_preconditions() retourne
#   Err(CalibrationPreconditionError(...)).
# - application/commands/run_calibration.py la propage telle quelle.
#---------------------------------------------------------------------->
