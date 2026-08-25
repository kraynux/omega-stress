# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Cycle de vie de l'application : fermeture propre des ressources partagees."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.app.dependency_container import DependencyContainer


@dataclass(frozen=True, slots=True)
class AppLifecycle:
    """Enveloppe le DependencyContainer avec les operations de cycle de
    vie qui lui sont propres (fermeture) — separe de sa construction
    (dependency_container.py::build_container), pour que "cabler" et
    "arreter proprement" restent deux responsabilites distinctes."""

    container: DependencyContainer

    def shutdown(self) -> None:
        """Ferme la connexion SQLite partagee. A appeler une seule fois,
        a la sortie normale du processus (voir app/bootstrap.py)."""
        self.container.connection.close()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'arret propre de l'application : ferme les ressources
#   partagees ouvertes par build_container() (aujourd'hui, la seule
#   ressource a fermer explicitement est la connexion SQLite).
# Pourquoi dans app/ (charte) :
# - "cycle de vie" au sens de ARCHITECTURE.md §2 : orchestration de
#   demarrage/arret, aucune regle metier.
# Ce qu'il ne contient PAS :
# - Aucune construction (voir dependency_container.py::build_container()).
# - Aucun flush explicite de l'AuditLogger/logger applicatif : ces deux
#   ecrivent en mode "append" a chaque appel (voir
#   infrastructure/logging/), rien a vider a la fermeture.
# Points cles :
# - shutdown() est idempotent au sens ou sqlite3.Connection.close() ne
#   leve pas si deja fermee — mais reste destine a n'etre appele qu'une
#   fois, au vrai arret du processus.
# Comment il sera utilise (apercu) :
# - interfaces/tui/app.py et interfaces/cli/main.py appellent
#   lifecycle.shutdown() dans un bloc finally, quelle que soit l'issue de
#   l'execution.
#---------------------------------------------------------------------->
