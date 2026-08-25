# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Query : lister les cibles epinglees et recentes."""
from __future__ import annotations

from omega_stress.application.dto.mappers import pinned_target_to_dto, target_to_dto
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.ports.target_repository import TargetRepository


def list_targets(
    *, target_repository: TargetRepository, recent_limit: int = 10
) -> tuple[TargetDTO, ...]:
    """Liste les cibles epinglees, puis les cibles recentes non deja
    epinglees (voir plan produit : "Cible : selection depuis liste
    epinglee, recente ou saisie controlee")."""
    pinned = target_repository.list_pinned()
    pinned_ids = {p.target.id for p in pinned}

    recent = target_repository.list_recent(limit=recent_limit)

    dtos = [pinned_target_to_dto(p) for p in pinned]
    dtos.extend(target_to_dto(t, pinned=False) for t in recent if t.id not in pinned_ids)
    return tuple(dtos)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Query en lecture seule combinant deux sources (cibles epinglees et
#   recentes) en une liste unique deduplique, sans effet de bord.
# Pourquoi dans application/queries/ (charte) :
# - Orchestration de deux appels au meme port sans modification d'etat.
# Ce qu'il ne contient PAS :
# - Aucune logique de deduplication complexe : une cible epinglee qui
#   apparaitrait aussi dans la liste des recentes est simplement exclue de
#   la seconde liste (comparaison d'id), pas fusionnee champ par champ.
# Points cles :
# - Les cibles epinglees apparaissent toujours en premier dans le resultat
#   (ordre de construction de `dtos`), coherent avec leur statut
#   privilegie dans le parcours utilisateur.
# Comment il sera utilise (apercu) :
# - interfaces/tui/widgets/target_picker.py.
#---------------------------------------------------------------------->
