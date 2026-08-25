# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Dispatch CLI scriptable — mode non interactif (cron, CI).

Ne demarre PAS l'application lui-meme (voir run()).
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from typing import TYPE_CHECKING

from omega_stress.core.constants import APP_NAME
from omega_stress.core.results import Err
from omega_stress.interfaces.cli.commands import (
    export_command,
    history_command,
    profile_command,
    run_command,
)
from omega_stress.interfaces.cli.formatters.text_formatter import format_error

if TYPE_CHECKING:
    # Import reserve au typage statique : jamais execute a l'import reel de
    # ce module (voir INFO DEV, "Ce qu'il ne contient PAS"), pour ne pas
    # tirer transitivement infrastructure/ (sqlite3/httpx/jinja2) dans
    # interfaces/, ce qu'import-linter interdit explicitement.
    from omega_stress.app.dependency_container import DependencyContainer


def build_parser() -> argparse.ArgumentParser:
    """Construit le parser racine et y enregistre les quatre
    sous-commandes (profile/run/history/export)."""
    parser = argparse.ArgumentParser(
        prog=APP_NAME, description="Test de charge HTTP encadre (mode scriptable)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_command.register(subparsers)
    run_command.register(subparsers)
    history_command.register(subparsers)
    export_command.register(subparsers)

    return parser


def run(container: DependencyContainer, argv: list[str] | None = None) -> int:
    """Parse argv et dispatche vers le handler de la sous-commande, avec
    un container DEJA construit (recu en parametre, jamais bati ici — voir
    src/omega_stress/__main__.py, la veritable racine de composition qui
    appelle app/bootstrap.py puis ce module)."""
    args = build_parser().parse_args(argv)

    try:
        result = asyncio.run(args.handler(args, container))
    except Exception as exc:  # filet de securite (ARCHITECTURE.md §5.4)
        print(format_error(f"erreur inattendue : {exc}"), file=sys.stderr)
        return 1

    if isinstance(result, Err):
        print(format_error(result.error), file=sys.stderr)
        return 1

    print(result.value)
    return 0

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Construit le parser CLI et dispatche vers le handler choisi par
#   argparse (via `set_defaults(handler=...)` dans chaque module de
#   commands/), affiche le resultat — ne demarre ni n'arrete
#   l'application.
# Pourquoi dans interfaces/cli/ (charte) :
# - Seul point d'arret ("filet de securite") cote CLI pour une exception
#   technique non prevue (ARCHITECTURE.md §5.4) : toute exception qui
#   n'est pas deja un Result.Err structure est interceptee ici, jamais
#   affichee comme une trace Python brute.
# Ce qu'il ne contient PAS :
# - Aucun appel a app/bootstrap.py : une premiere version de ce fichier
#   appelait bootstrap() directement, ce qui rendait interfaces/
#   transitivement dependante d'infrastructure/ (sqlite3, httpx, jinja2)
#   — viole a la fois le contrat d'independance interfaces/infrastructure
#   et les contrats "X seulement dans Y", detecte par import-linter en
#   pratique. Le demarrage/arret de l'application est desormais du
#   ressort exclusif de src/omega_stress/__main__.py, la VRAIE racine de
#   composition (au-dessus de app/ ET interfaces/, elle n'appartient a
#   aucune des deux couches et n'est donc contrainte par aucun contrat de
#   couches).
# - Aucun import runtime de DependencyContainer : le type n'est importe
#   que sous `TYPE_CHECKING` (voir en tete de fichier), invisible a
#   l'execution et au graphe de dependances analyse par import-linter.
# - Aucun import `textual` (verifie par le contrat import-linter
#   "textual seulement dans interfaces.tui", qui liste explicitement
#   interfaces.cli comme source interdite).
# Points cles :
# - asyncio.run() : tous les handlers sont `async def` par convention
#   (voir profile_command.py, INFO DEV), qu'ils appellent ou non une
#   fonction reellement asynchrone en dessous — un seul point
#   d'orchestration asyncio dans tout le CLI.
# - args.handler est pose par argparse via `set_defaults()` dans chaque
#   module de commands/ : ce fichier n'a pas besoin de connaitre la
#   sous-commande precise, juste d'appeler le handler qu'argparse a
#   selectionne.
# Comment il sera utilise (apercu) :
# - src/omega_stress/__main__.py appelle bootstrap() puis run(container,
#   argv), et ferme le cycle de vie dans un `finally`.
#---------------------------------------------------------------------->
