# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Query : lister l'historique des runs, avec filtres optionnels."""
from __future__ import annotations

from omega_stress.application.dto.mappers import run_to_dto
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.domain.runs.models import LoadRun
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository


def list_history(
    *,
    run_repository: RunRepository,
    target_repository: TargetRepository,
    target_id: str | None = None,
    profile_id: str | None = None,
    limit: int = 50,
) -> tuple[RunDTO, ...]:
    """Liste l'historique des runs, filtrable par cible et/ou profil (voir
    plan produit, "Historique et exports")."""
    runs = run_repository.list_history(target_id=target_id, profile_id=profile_id, limit=limit)
    return tuple(_to_dto_with_address(r, target_repository=target_repository) for r in runs)


def _to_dto_with_address(run: LoadRun, *, target_repository: TargetRepository) -> RunDTO:
    target = target_repository.get(run.target_id)
    target_address = target.address.base_url if target is not None else run.target_id
    return run_to_dto(run, target_address=target_address)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Query en lecture seule, transmet les filtres directement au
#   repository (aucun filtrage cote application).
# Pourquoi dans application/queries/ (charte) :
# - Aucune modification d'etat.
# Ce qu'il ne contient PAS :
# - Aucun filtre par date ou par type de test explicite (voir
#   ports/run_repository.py, meme limitation documentee) : a etendre si
#   un besoin de filtrage plus fin est confirme par le produit.
# Points cles :
# - target_id et profile_id peuvent etre combines (ET logique) : la
#   semantique exacte de la combinaison est de la responsabilite de
#   l'implementation du port, pas de cette query.
# - _to_dto_with_address() (2026-08-25) : une resolution target_repository
#   PAR RUN (N+1 requetes sur la liste retournee) — accepte deliberement,
#   `limit` reste borne (50 par defaut) et target_repository.get() est une
#   lecture locale SQLite, pas un appel reseau ; meme raison et meme
#   resolution que application/queries/get_run_details.py (voir son INFO
#   DEV pour le bug rapporte a l'origine).
# Comment il sera utilise (apercu) :
# - interfaces/tui/widgets/history_table.py,
#   interfaces/cli/commands/history_command.py.
#---------------------------------------------------------------------->
