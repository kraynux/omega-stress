# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sous-commande CLI `history` : lister et consulter le detail d'un run."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_stress.application.queries.get_run_details import get_run_details
from omega_stress.application.queries.list_history import list_history
from omega_stress.core.results import Err, Ok, Result
from omega_stress.interfaces.cli.formatters.text_formatter import (
    format_run,
    format_run_list,
    to_json,
)

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/main.py pour
    # la justification complete) : jamais execute a l'import reel.
    from omega_stress.app.dependency_container import DependencyContainer


def _json_flag_parent() -> argparse.ArgumentParser:
    """Voir profile_command.py::_json_flag_parent() pour la justification
    (meme fragment, duplique volontairement : chaque module de commande
    reste autonome, pas de fichier partage pour 4 lignes)."""
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    return parent


def register(subparsers: argparse._SubParsersAction) -> None:
    """Enregistre `history list|show` sur le parser CLI."""
    parser = subparsers.add_parser("history", help="Consulter l'historique des runs")
    actions = parser.add_subparsers(dest="history_action", required=True)

    list_parser = actions.add_parser(
        "list", help="Lister l'historique, filtrable", parents=[_json_flag_parent()]
    )
    list_parser.add_argument("--target-id", default=None)
    list_parser.add_argument("--profile-id", default=None)
    list_parser.add_argument("--limit", type=int, default=50)
    list_parser.set_defaults(handler=_handle_list)

    show_parser = actions.add_parser(
        "show", help="Afficher le detail d'un run", parents=[_json_flag_parent()]
    )
    show_parser.add_argument("run_id")
    show_parser.set_defaults(handler=_handle_show)


async def _handle_list(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    runs = list_history(
        run_repository=container.run_repository,
        target_repository=container.target_repository,
        target_id=args.target_id,
        profile_id=args.profile_id,
        limit=args.limit,
    )
    return Ok(to_json(runs) if args.json else format_run_list(runs))


async def _handle_show(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    run = get_run_details(
        args.run_id,
        run_repository=container.run_repository,
        target_repository=container.target_repository,
    )
    if run is None:
        return Err(f"Run {args.run_id!r} introuvable.")
    return Ok(to_json(run) if args.json else format_run(run))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit `omega-stress history list|show` en appels aux queries
#   list_history/get_run_details.
# Pourquoi dans interfaces/cli/commands/ (charte) :
# - Adaptateur de presentation scriptable, aucune logique propre.
# Ce qu'il ne contient PAS :
# - Aucun filtre supplementaire (date, type de test) : meme limitation que
#   ports/run_repository.py et application/queries/list_history.py,
#   deja documentee a ces niveaux.
# Points cles :
# - `show` retourne un Err (pas une exception) pour un run_id inconnu :
#   get_run_details() renvoie None sur absence (une recherche normale,
#   pas un echec metier), traduit ici en message explicite pour
#   l'utilisateur CLI plutot que de propager le None silencieusement.
# - target_repository (2026-08-25) : list_history()/get_run_details()
#   resolvent desormais RunDTO.target_address (adresse humaine plutot que
#   l'id parfois opaque d'une cible epinglee) — voir leur INFO DEV
#   respectif.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py appelle register() au demarrage.
#---------------------------------------------------------------------->
