# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de publication de la progression d'un run vers la presentation."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.runs.models import IntervalSample


class RunProgressNotifier(Protocol):
    """Port consomme par application/pipeline/executor.py, implemente
    cote infrastructure et cote presentation (voir Comment il sera
    utilise), jamais accede directement par interfaces/tui/ sans passer
    par cette abstraction."""

    def notify(self, run_id: str, sample: IntervalSample) -> None:
        """Publie un point de progression. Ne bloque jamais sur le
        rendu : l'implementation est responsable de tout decouplage
        necessaire (ex. file interne consommee par le progress_panel)."""
        ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul canal autorise entre l'execution d'un run et son affichage en
#   direct, formalisant la regle "Aucun acces direct de presentation a
#   l'objet runner" (ARCHITECTURE.md §5, "Regle de generation de charge").
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (publier un point de mesure), jamais
#   par l'API interne de Textual (pas de reference a un widget ou un
#   message Textual dans ce contrat).
# Ce qu'il ne contient PAS :
# - Aucune implementation (voir infrastructure/, qui adapte ce port vers
#   un mecanisme concret consomme par interfaces/tui/widgets/
#   progress_panel.py — le detail de cablage TUI reste hors de ports/).
# - Aucune notion d'abonnement/desabonnement : un seul run actif a la fois
#   en V1 (mono-utilisateur local), pas de gestion multi-abonnes.
# Points cles :
# - notify() est appelee tres frequemment (1 fois par seconde par run
#   actif) : l'implementation doit rester non bloquante, jamais faire
#   d'I/O lourde synchrone dans ce chemin chaud.
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle notify() a chaque
#   IntervalSample recu du port load_runner.
# - application/pipeline/hooks/metrics_hook.py peut egalement s'appuyer
#   sur ce port pour relayer une metrique agregee.
#---------------------------------------------------------------------->
