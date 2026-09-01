# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de publication de la progression PENDANT un palier de calibrage."""
from __future__ import annotations

from typing import Protocol


class CalibrationStageProgressNotifier(Protocol):
    """Port consomme par infrastructure/calibration/stage_runner.py,
    implemente cote presentation — meme role que ports/run_progress_
    notifier.py::RunProgressNotifier pour un run reel, mais pour UN
    palier de calibrage (pas d'IntervalSample equivalent, un palier ne
    produit qu'une seule StageMeasurement a la toute fin)."""

    def notify(self, stage_id: str, elapsed_seconds: int, window_seconds: int) -> None:
        """Publie l'avancement PENDANT un palier, une fois par seconde
        ecoulee (1 <= elapsed_seconds <= window_seconds). Ne bloque
        jamais sur le rendu, meme convention que RunProgressNotifier."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul canal autorise entre l'execution d'un palier de calibrage et son
#   affichage en direct SECONDE PAR SECONDE — distinct du NotificationSink
#   deja utilise par application/commands/run_calibration.py (qui ne
#   publie qu'une fois par palier TERMINE, jamais pendant).
# Pourquoi dans ports/ (charte) :
# - Meme raisonnement que ports/run_progress_notifier.py : defini par le
#   besoin applicatif (publier un point d'avancement), jamais par l'API
#   interne de Textual.
# Ce qu'il ne contient PAS :
# - Aucune implementation (voir interfaces/tui/screens/calibration_
#   screen.py, qui adapte ce port vers widgets/run_progress.py, deja
#   reutilise tel quel — un palier de calibrage se presente comme
#   n'importe quel autre avancement temporel du point de vue de l'ecran).
# Points cles :
# - Bug reel rapporte (2026-09-02, captures d'ecran : "le calibrage
#   semble geler... la jauge n'avance plus") : avant ce port, un palier
#   qui prenait plus de temps que prevu (meme limite de capacite locale
#   que Test connexions Agressif, voir domain/load/policies.py::
#   GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL) ne produisait AUCUN
#   signal d'avancement avant sa toute fin — indiscernable d'un vrai gel
#   depuis l'ecran. Ce port comble cet ecart de granularite.
# Comment il sera utilise (apercu) :
# - infrastructure/calibration/stage_runner.py::HttpxCalibrationStageRunner
#   .run_stage() appelle notify() a chaque seconde de sa boucle interne.
# - application/commands/run_calibration.py recoit ce port en parametre et
#   le transmet tel quel a runner.run_stage(), sans jamais l'interpreter
#   lui-meme (comme run_progress_notifier pour un run reel).
#---------------------------------------------------------------------->
