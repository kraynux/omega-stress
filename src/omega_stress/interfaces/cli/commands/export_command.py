# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sous-commande CLI `export` : exporter le rapport d'un run termine."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_stress.application.commands.export_run_report import export_run_report
from omega_stress.application.dto.export_dto import ExportRequestDTO
from omega_stress.core.enums import ExportFormat
from omega_stress.core.results import Err, Ok, Result
from omega_stress.interfaces.cli.formatters.text_formatter import format_export_result, to_json
from omega_stress.shared.clock import utc_now
from omega_stress.shared.ids import new_id

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/main.py pour
    # la justification complete) : jamais execute a l'import reel.
    from omega_stress.app.dependency_container import DependencyContainer


def register(subparsers: argparse._SubParsersAction) -> None:
    """Enregistre `export <run-id> --format ... --destination ...` sur le
    parser CLI."""
    parser = subparsers.add_parser("export", help="Exporter le rapport d'un run termine")
    parser.add_argument("run_id")
    parser.add_argument("--format", required=True, choices=[fmt.value for fmt in ExportFormat])
    parser.add_argument("--destination", required=True)
    parser.add_argument("--theme", default="omega-base")
    parser.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    parser.set_defaults(handler=_handle_export)


async def _handle_export(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    request = ExportRequestDTO(
        run_id=args.run_id,
        format=args.format,
        destination_path=args.destination,
        export_theme=args.theme,
    )
    result = await export_run_report(
        request,
        run_repository=container.run_repository,
        target_repository=container.target_repository,
        export_repository=container.export_repository,
        exporters=container.exporters,
        id_factory=new_id,
        now=utc_now(),
    )
    if isinstance(result, Err):
        return Err(str(result.error))
    return Ok(to_json(result.value) if args.json else format_export_result(result.value))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit `omega-stress export <run-id> --format ... --destination ...`
#   en appel a application/commands/export_run_report.py.
# Pourquoi dans interfaces/cli/commands/ (charte) :
# - Adaptateur de presentation scriptable, aucune logique propre —
#   couvre l'objectif "mode non interactif scriptable... consulter/
#   exporter l'historique" du plan produit.
# Ce qu'il ne contient PAS :
# - Aucune selection d'exporter concret : container.exporters (construit
#   par app/dependency_container.py) fournit deja le mapping complet
#   ExportFormat -> ReportExporter, ce fichier le transmet tel quel.
# Points cles :
# - --theme n'a d'effet reel que pour --format html (voir
#   domain/reports/service.py::requires_theme()) : transmis
#   inconditionnellement, ignore silencieusement par les exporters
#   JSON/CSV.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py appelle register() au demarrage.
#---------------------------------------------------------------------->
