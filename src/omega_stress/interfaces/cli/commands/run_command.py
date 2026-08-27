# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sous-commande CLI `run` : precheck, request, connection, ramp, replay."""
from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from omega_stress.application.commands.replay_run import replay_run
from omega_stress.application.commands.run_connection_load import run_connection_load
from omega_stress.application.commands.run_precheck import run_precheck
from omega_stress.application.commands.run_ramp_load import run_ramp_load
from omega_stress.application.commands.run_request_load import run_request_load
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.interfaces.cli.formatters.text_formatter import format_run, to_json
from omega_stress.shared.clock import utc_now
from omega_stress.shared.ids import new_id

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/main.py pour
    # la justification complete) : jamais execute a l'import reel.
    from omega_stress.app.dependency_container import DependencyContainer


class _CliProgressNotifier:
    """Notifier minimal pour le mode CLI : affiche une ligne de
    progression compacte sur stderr, jamais stdout (reserve au resultat
    final structure, voir ARCHITECTURE.md et la convention Unix : sortie
    utile sur stdout, incidentel sur stderr)."""

    def notify(self, run_id: str, sample: IntervalSample) -> None:
        sys.stderr.write(
            f"\r[{run_id}] t={sample.at_second:.0f}s "
            f"req={sample.request_count} err={sample.error_count} "
            f"p95={sample.p95_latency_ms:.0f}ms   "
        )
        sys.stderr.flush()


def register(subparsers: argparse._SubParsersAction) -> None:
    """Enregistre `run precheck|request|connection|ramp|replay` sur le
    parser CLI."""
    parser = subparsers.add_parser("run", help="Lancer un test de charge")
    actions = parser.add_subparsers(dest="run_action", required=True)

    precheck_parser = actions.add_parser("precheck", help="Lancer un Pre-check")
    precheck_parser.add_argument("--target-id", required=True)
    precheck_parser.add_argument("--target-url", required=True)
    precheck_parser.add_argument("--confirm", action="store_true")
    precheck_parser.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    precheck_parser.set_defaults(handler=_handle_precheck)

    request_parser = actions.add_parser("request", help="Lancer un Test requetes")
    _add_load_launch_arguments(request_parser)
    request_parser.set_defaults(handler=_handle_request)

    connection_parser = actions.add_parser("connection", help="Lancer un Test connexions")
    _add_load_launch_arguments(connection_parser)
    connection_parser.set_defaults(handler=_handle_connection)

    ramp_parser = actions.add_parser("ramp", help="Lancer un Test charge (montee progressive)")
    _add_load_launch_arguments(ramp_parser)
    ramp_parser.set_defaults(handler=_handle_ramp)

    replay_parser = actions.add_parser("replay", help="Rejouer un run existant")
    replay_parser.add_argument("run_id")
    replay_parser.add_argument("--confirm", action="store_true")
    replay_parser.add_argument("--precheck-validated", action="store_true")
    replay_parser.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    replay_parser.set_defaults(handler=_handle_replay)


def _add_load_launch_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--level", required=True, choices=[level.value for level in IntensityLevel])
    parser.add_argument("--duration-minutes", required=True, type=int)
    parser.add_argument("--max-error-rate", required=True, type=float)
    parser.add_argument("--max-p95-latency-ms", type=float, default=None)
    parser.add_argument("--profile-id", default=None)
    parser.add_argument(
        "--confirm", action="store_true", help="Confirme l'autorisation d'usage de la cible"
    )
    parser.add_argument("--precheck-validated", action="store_true")
    parser.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )


async def _handle_precheck(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    result = await run_precheck(
        target_id=args.target_id,
        target_url=args.target_url,
        target_repository=container.target_repository,
        load_runner=container.load_runner,
        run_progress_notifier=_CliProgressNotifier(),
        run_repository=container.run_repository,
        audit_sink=container.audit_logger.record,
        notification_sink=_print_notification,
        id_factory=new_id,
        explicit_confirmation=args.confirm,
        now=utc_now,
    )
    sys.stderr.write("\n")
    return _finish(result, args)


async def _handle_request(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    result = await run_request_load(**_load_kwargs(args, container))
    sys.stderr.write("\n")
    return _finish(result, args)


async def _handle_connection(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    result = await run_connection_load(**_load_kwargs(args, container))
    sys.stderr.write("\n")
    return _finish(result, args)


async def _handle_ramp(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    result = await run_ramp_load(**_load_kwargs(args, container))
    sys.stderr.write("\n")
    return _finish(result, args)


async def _handle_replay(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    _ensure_capabilities_probed(container)
    result = await replay_run(
        args.run_id,
        run_repository=container.run_repository,
        profile_repository=container.profile_repository,
        target_repository=container.target_repository,
        load_runner=container.load_runner,
        run_progress_notifier=_CliProgressNotifier(),
        audit_sink=container.audit_logger.record,
        notification_sink=_print_notification,
        id_factory=new_id,
        explicit_confirmation=args.confirm,
        precheck_validated=args.precheck_validated,
        now=utc_now,
        capability_registry=container.capability_registry,
    )
    sys.stderr.write("\n")
    return _finish(result, args)


def _ensure_capabilities_probed(container: DependencyContainer) -> None:
    """Peuple core/capability_registry.py depuis un sondage frais avant
    tout lancement — sans cela, un lancement Haut/Maximum leverait
    CapabilityRegistryError (capacite jamais enregistree) au lieu d'un
    refus controle, alors que le pre-flight check est cense produire
    exactement ce refus explicite (voir plan produit, "Configuration
    minimale du generateur")."""
    for capability in container.system_probe.probe():
        container.capability_registry.register(capability)


def _load_kwargs(args: argparse.Namespace, container: DependencyContainer) -> dict:
    _ensure_capabilities_probed(container)
    return dict(
        target_id=args.target_id,
        target_url=args.target_url,
        level=IntensityLevel(args.level),
        duration_minutes=args.duration_minutes,
        thresholds=Thresholds(
            max_error_rate=args.max_error_rate, max_p95_latency_ms=args.max_p95_latency_ms
        ),
        explicit_confirmation=args.confirm,
        precheck_validated=args.precheck_validated,
        profile_id=args.profile_id,
        target_repository=container.target_repository,
        load_runner=container.load_runner,
        run_progress_notifier=_CliProgressNotifier(),
        run_repository=container.run_repository,
        audit_sink=container.audit_logger.record,
        notification_sink=_print_notification,
        id_factory=new_id,
        now=utc_now,
        capability_registry=container.capability_registry,
    )


def _print_notification(message: str) -> None:
    print(message, file=sys.stderr)


def _finish(result: Result, args: argparse.Namespace) -> Result[str, str]:
    if isinstance(result, Err):
        return Err(str(result.error))
    return Ok(to_json(result.value) if args.json else format_run(result.value))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit `omega-stress run precheck|request|connection|ramp|replay` en
#   appels aux cinq commands d'execution de application/commands/.
# Pourquoi dans interfaces/cli/commands/ (charte) :
# - Adaptateur de presentation scriptable, sans Textual — c'est le seul
#   command CLI qui declenche une execution reelle (les autres ne font
#   que lire/creer des donnees legeres).
# Ce qu'il ne contient PAS :
# - Aucune logique de guard/pipeline (deja dans application/pipeline/) :
#   ce fichier ne fait qu'assembler les parametres et appeler le command.
# - Aucun sondage de capacite systeme actif : container.capability_registry
#   est transmis tel quel (potentiellement vide en debut de processus) —
#   le peuplement depuis infrastructure/probe/local_probe.py n'est pas
#   encore cable ici, a faire quand un besoin reel de blocage Haut/Maximum
#   sur capacite sera exerce en pratique (le guard reste fonctionnel avec
#   un registre vide : capability_guard leve CapabilityRegistryError sur
#   une capacite jamais enregistree, ce qui bloque prudemment plutot que
#   de laisser passer).
# Points cles :
# - _CliProgressNotifier ecrit sur stderr avec \r (mise a jour sur place),
#   jamais sur stdout : la convention CLI Unix reserve stdout au resultat
#   final structure (redirigeable/parsable), stderr a l'incidentel.
# - _load_kwargs() factorise les arguments identiques entre request/
#   connection/ramp (memes options CLI, seule la fonction appelee
#   differe) — evite de dupliquer un dict de 15 champs trois fois.
# - _finish() est le point unique de traduction Result[RunDTO, ...] ->
#   Result[str, str], reutilise par les cinq handlers.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py appelle register() au demarrage.
#---------------------------------------------------------------------->
