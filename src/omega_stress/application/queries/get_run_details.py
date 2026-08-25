# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Query : recuperer le detail d'un run par id."""
from __future__ import annotations

from omega_stress.application.dto.mappers import run_to_dto
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.ports.run_repository import RunRepository
from omega_stress.ports.target_repository import TargetRepository


def get_run_details(
    run_id: str, *, run_repository: RunRepository, target_repository: TargetRepository
) -> RunDTO | None:
    """Retourne le detail d'un run, ou None s'il n'existe pas (l'absence
    d'un run n'est pas un echec metier a traiter via Result, c'est un
    resultat de recherche normal)."""
    run = run_repository.get(run_id)
    if run is None:
        return None
    target = target_repository.get(run.target_id)
    target_address = target.address.base_url if target is not None else run.target_id
    return run_to_dto(run, target_address=target_address)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Query en lecture seule pour l'ecran "Detail d'un run" du plan produit.
# Pourquoi dans application/queries/ (charte) :
# - Aucune modification d'etat.
# Ce qu'il ne contient PAS :
# - Aucun ReportContent complet (diagnostic avec recommandations
#   construites) : ce niveau de detail reste construit a la demande par
#   domain/reports/builders.py au moment d'un export, pas precalcule ici
#   pour un simple affichage d'ecran (evite un couplage inutile entre
#   l'ecran de detail et le sous-domaine reports). RunDTO.events (bruts,
#   directement relayes depuis LoadResult.events par
#   application/dto/mappers.py::run_to_dto()) reste dans ce cas : ce n'est
#   pas un ReportContent, juste assez pour afficher la raison d'un
#   echec/arret automatique sans construire de diagnostic complet.
#   RunDTO.samples (2026-08-24, voir son propre INFO DEV) EST desormais
#   inclus — un simple miroir plat de LoadResult.samples, pas un
#   ReportContent non plus.
# Points cles :
# - Retourne None plutot qu'un Result ou une exception pour un id
#   inconnu : coherent avec le style "recherche" plutot que "commande" de
#   cette query (voir ports/run_repository.py::get(), meme convention).
# - target_repository (2026-08-25) : resout run.target_id (potentiellement
#   un id opaque pour une cible epinglee, voir application/dto/
#   run_dto.py::RunDTO.target_address) en adresse humaine, MEME PATRON que
#   application/commands/export_run_report.py (target_repository.get(),
#   repli sur target_id brut si la cible a ete supprimee depuis) — bug
#   reel rapporte ("si on choisit une epingle... on a le numero
#   657000045dbgr4100346... comment savoir c'est quelle cible ?").
# Comment il sera utilise (apercu) :
# - interfaces/tui/screens/run_details.py,
#   interfaces/cli/commands/history_command.py.
#---------------------------------------------------------------------->
