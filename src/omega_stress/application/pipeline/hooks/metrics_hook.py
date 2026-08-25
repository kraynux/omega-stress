# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Hook : republie chaque mesure d'intervalle vers la presentation, en cours d'execution."""
from __future__ import annotations

from omega_stress.domain.runs.models import IntervalSample
from omega_stress.ports.run_progress_notifier import RunProgressNotifier


def publish_sample(run_id: str, sample: IntervalSample, *, notifier: RunProgressNotifier) -> None:
    """Republie un IntervalSample vers la presentation via le port
    run_progress_notifier — seul chemin autorise entre l'execution d'un
    run et son affichage en direct (ARCHITECTURE.md §5, "Regle de
    generation de charge")."""
    notifier.notify(run_id, sample)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul hook execute EN CONTINU pendant le run (les deux autres,
#   audit_hook et notification_hook, s'executent apres coup ou sur
#   evenement ponctuel) : republie chaque mesure vers run_progress_notifier.
# Pourquoi dans application/pipeline/hooks/ (charte) :
# - Point d'integration nomme explicitement dans le pipeline
#   (ARCHITECTURE.md §4, etape 8 "hooks... en cours pour les metriques"),
#   plutot qu'un appel direct au port depuis executor.py — garde la
#   possibilite d'enrichir plus tard (ex. filtrage, throttling
#   d'affichage) sans toucher executor.py.
# Ce qu'il ne contient PAS :
# - Aucune evaluation de seuil (deja faite separement par
#   application/pipeline/guards/threshold_guard.py, appele en parallele
#   par executor.py sur le meme IntervalSample).
# - Aucune implementation de notifier (voir infrastructure/, qui adapte
#   ce port vers un mecanisme concret consomme par
#   interfaces/tui/widgets/progress_panel.py).
# Points cles :
# - Fonction intentionnellement mince, sans etat : republie chaque
#   mesure telle quelle, aucune agregation (celle-ci vit dans
#   domain/runs/service.py::aggregate_samples(), appelee separement en
#   fin d'execution).
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle publish_sample() a chaque
#   IntervalSample recu, juste apres l'evaluation de seuil.
#---------------------------------------------------------------------->
