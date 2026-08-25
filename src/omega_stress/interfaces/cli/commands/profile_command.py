# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sous-commande CLI `profile` : lister, creer, figer un profil."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_stress.application.commands.create_profile import create_profile
from omega_stress.application.commands.freeze_profile import freeze_profile
from omega_stress.application.queries.list_profiles import list_profiles
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.interfaces.cli.formatters.text_formatter import (
    format_profile,
    format_profile_list,
    to_json,
)
from omega_stress.shared.clock import utc_now
from omega_stress.shared.ids import new_id

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/main.py pour
    # la justification complete) : jamais execute a l'import reel.
    from omega_stress.app.dependency_container import DependencyContainer


def _json_flag_parent() -> argparse.ArgumentParser:
    """Fragment de parser partage par chaque sous-commande terminale, pour
    que `--json` reste valide place APRES la sous-commande (ex. `profile
    list --json`), pas seulement avant — argparse n'accepte un argument
    que sur le parser exact qui le declare, jamais herite implicitement
    d'un parser parent."""
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    return parent


def register(subparsers: argparse._SubParsersAction) -> None:
    """Enregistre `profile list|create|freeze` sur le parser CLI."""
    parser = subparsers.add_parser("profile", help="Gerer les profils de test")
    actions = parser.add_subparsers(dest="profile_action", required=True)

    list_parser = actions.add_parser(
        "list", help="Lister les profils", parents=[_json_flag_parent()]
    )
    list_parser.add_argument("--include-archived", action="store_true")
    list_parser.set_defaults(handler=_handle_list)

    create_parser = actions.add_parser(
        "create", help="Creer un profil non fige", parents=[_json_flag_parent()]
    )
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--description", default="")
    create_parser.add_argument("--target-id", required=True)
    create_parser.add_argument("--family", required=True, choices=[f.value for f in TestFamily])
    create_parser.add_argument(
        "--level", required=True, choices=[level.value for level in IntensityLevel]
    )
    create_parser.add_argument("--duration-minutes", required=True, type=int)
    create_parser.add_argument("--max-error-rate", required=True, type=float)
    create_parser.add_argument("--max-p95-latency-ms", type=float, default=None)
    create_parser.add_argument("--tags", default="", help="Liste separee par des virgules")
    create_parser.add_argument("--extended-duration-authorized", action="store_true")
    create_parser.set_defaults(handler=_handle_create)

    freeze_parser = actions.add_parser(
        "freeze", help="Figer un profil existant", parents=[_json_flag_parent()]
    )
    freeze_parser.add_argument("profile_id")
    freeze_parser.set_defaults(handler=_handle_freeze)


async def _handle_list(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    profiles = list_profiles(
        profile_repository=container.profile_repository, include_archived=args.include_archived
    )
    return Ok(to_json(profiles) if args.json else format_profile_list(profiles))


async def _handle_create(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    tags = tuple(tag.strip() for tag in args.tags.split(",") if tag.strip())
    result = create_profile(
        profile_repository=container.profile_repository,
        id_factory=new_id,
        now=utc_now(),
        name=args.name,
        description=args.description,
        default_target_id=args.target_id,
        family=TestFamily(args.family),
        level=IntensityLevel(args.level),
        duration_minutes=args.duration_minutes,
        max_error_rate=args.max_error_rate,
        max_p95_latency_ms=args.max_p95_latency_ms,
        tags=tags,
        extended_duration_authorized=args.extended_duration_authorized,
    )
    if isinstance(result, Err):
        return Err(str(result.error))
    return Ok(to_json(result.value) if args.json else format_profile(result.value))


async def _handle_freeze(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    result = freeze_profile(
        args.profile_id, profile_repository=container.profile_repository, now=utc_now()
    )
    if isinstance(result, Err):
        return Err(str(result.error))
    return Ok(to_json(result.value) if args.json else format_profile(result.value))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit `omega-stress profile list|create|freeze` en appels aux
#   commands/queries deja existants de application/ — aucune regle
#   metier reecrite ici (ARCHITECTURE.md §2, §10 : "une commande CLI
#   appelle un command/query existant, jamais une logique reecrite").
# Pourquoi dans interfaces/cli/commands/ (charte) :
# - Adaptateur de presentation scriptable, sans Textual.
# Ce qu'il ne contient PAS :
# - Aucun import `textual` (verifie par le contrat import-linter).
# - Aucune verification que create_profile()/freeze_profile() sont
#   valides : ce fichier transmet les arguments tels quels, toute la
#   validation reste dans domain/profiles/validation.py, invoquee par le
#   command lui-meme.
# Points cles :
# - Chaque handler retourne Result[str, str] (texte deja forme, ou
#   message d'erreur) : interfaces/cli/main.py gere l'affichage et le
#   code de sortie de facon uniforme, sans connaitre le detail de chaque
#   sous-commande.
# - args.json (flag global, defini par interfaces/cli/main.py) bascule
#   entre sortie humaine (format_profile*) et sortie machine (to_json) —
#   la meme donnee, deux representations, jamais deux chemins de calcul.
# - create_profile()/freeze_profile() sont des fonctions SYNCHRONES (pas
#   de I/O asynchrone dans leur chemin) ; les handlers restent `async def`
#   par uniformite avec les commands run_*_load (asynchrones), pour que
#   interfaces/cli/main.py dispatche tous les handlers de la meme facon
#   (`await args.handler(...)`), quelle que soit la sous-commande.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py appelle register() au demarrage.
#---------------------------------------------------------------------->
