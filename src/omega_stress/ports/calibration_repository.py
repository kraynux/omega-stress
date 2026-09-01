# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de persistance d'un CalibrationResult, garde par empreinte
machine (voir document produit, "Persistance et compatibilite")."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.calibration.models import CalibrationResult


class CalibrationRepository(Protocol):
    """Implemente par infrastructure/storage/files/
    json_calibration_store.py — UN resultat persiste par empreinte
    machine (fingerprint_hash), jamais un historique de plusieurs
    calibrages pour la meme machine (un nouveau calibrage REMPLACE le
    precedent pour cette empreinte, voir save())."""

    def save(self, result: CalibrationResult) -> None:
        """Persiste result, ecrase tout resultat precedent pour la meme
        empreinte (result.fingerprint)."""
        ...

    def load(self, fingerprint_hash: str) -> CalibrationResult | None:
        """None si aucun calibrage n'a jamais ete persiste pour cette
        empreinte — jamais une erreur, un poste jamais calibre est un
        cas normal."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de persistance d'un resultat de calibrage complet.
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (sauvegarder/relire un
#   CalibrationResult par empreinte), jamais par le format de stockage
#   concret (JSON) — meme raisonnement que ports/settings_store.py.
# Ce qu'il ne contient PAS :
# - Aucun calcul d'empreinte (voir infrastructure/calibration/
#   fingerprint.py) : ce port recoit un fingerprint_hash deja calcule,
#   jamais un CalibrationFingerprint brut a hacher lui-meme.
# - Aucune notion d'historique/liste : un seul resultat par empreinte,
#   coherent avec le document ("un calibrage est invalide si le moteur,
#   le nombre de CPU utilisables, la RAM... a change" — un changement de
#   machine/config appelle un NOUVEAU calibrage, pas un archivage de
#   l'ancien).
# Comment il sera utilise (apercu) :
# - application/commands/run_calibration.py appelle save() a la fin de
#   la progression.
# - interfaces/tui/screens/calibration_screen.py appelle load() pour
#   afficher le dernier resultat connu au montage.
#---------------------------------------------------------------------->
