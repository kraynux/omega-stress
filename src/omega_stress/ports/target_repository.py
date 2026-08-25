# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de persistance des cibles (recentes et epinglees)."""
from __future__ import annotations

from typing import Protocol

from omega_stress.domain.targets.models import PinnedTarget, Target


class TargetRepository(Protocol):
    """Port consomme par application/, implemente par
    infrastructure/storage/sqlite/target_repository.py."""

    def save_recent(self, target: Target) -> None: ...

    def save_pinned(self, pinned: PinnedTarget) -> None: ...

    def get(self, target_id: str) -> Target | None: ...

    def get_pinned(self, target_id: str) -> PinnedTarget | None: ...

    def list_pinned(self) -> tuple[PinnedTarget, ...]: ...

    def list_recent(self, *, limit: int = 10) -> tuple[Target, ...]: ...

    def unpin(self, target_id: str) -> None: ...

    def clear_recent(self) -> None: ...

    def clear_all(self) -> None: ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat de persistance des cibles, distinguant recentes (saisies
#   ponctuelles) et epinglees (autorisees de facon persistante).
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin du panneau de tests ("cible : selection depuis
#   liste epinglee, recente ou saisie controlee"), pas par une table SQL
#   precise.
# Ce qu'il ne contient PAS :
# - Aucune implementation concrete.
# - Aucune verification d'autorisation (deja actee au moment ou
#   save_pinned() est appele, via domain/targets/service.py::pin() en
#   amont — ce port ne fait que persister le resultat).
# Points cles :
# - get(target_id) resout une cible quel que soit son statut (epinglee ou
#   simplement recente) — distinct de get_pinned(), qui ne retourne
#   quelque chose que pour une cible AUTORISEE de facon persistante. Un
#   appelant qui a seulement besoin de l'adresse d'affichage (ex. un
#   export de rapport) utilise get(), jamais get_pinned() pour ca.
# - get_pinned(target_id) retourne None si la cible n'est pas (ou plus)
#   epinglee, jamais une exception : l'absence d'epinglage est un etat
#   normal, pas une erreur.
# - unpin() est une simple suppression, sans regle metier associee (voir
#   domain/targets/service.py, qui ne definit volontairement pas de
#   fonction unpin()).
# - clear_recent()/clear_all() (2026-08-24) : deux purges distinctes,
#   demandees explicitement pour l'ecran Reglages. clear_recent() ne
#   touche que la table targets (cibles recentes non epinglees) ; les
#   cibles epinglees representent une autorisation deliberee, jamais
#   effacee par une purge "recentes seulement". clear_all() efface les
#   deux tables (recentes ET epinglees) — reperd les autorisations, exige
#   une confirmation dediee cote ecran (voir screens/confirm.py).
# Comment il sera utilise (apercu) :
# - application/commands/pin_target.py, unpin_target.py et
#   application/queries/list_targets.py.
# - application/commands/export_run_report.py et replay_run.py appellent
#   get() pour resoudre l'adresse d'une cible a partir du target_id
#   enregistre sur un LoadRun.
#---------------------------------------------------------------------->
