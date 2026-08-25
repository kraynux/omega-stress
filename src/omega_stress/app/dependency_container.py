# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Assemblage manuel des adaptateurs concrets derriere les ports (pas de framework DI)."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import ExportFormat
from omega_stress.infrastructure.config import paths
from omega_stress.infrastructure.exporters.csv_exporter import CsvReportExporter
from omega_stress.infrastructure.exporters.html_exporter import HtmlReportExporter
from omega_stress.infrastructure.exporters.json_exporter import JsonReportExporter
from omega_stress.infrastructure.logging.audit_logger import AuditLogger
from omega_stress.infrastructure.probe.local_probe import LocalSystemProbe
from omega_stress.infrastructure.runner.httpx_load_generator import HttpxLoadGenerator
from omega_stress.infrastructure.storage.files.json_settings_store import JsonSettingsStore
from omega_stress.infrastructure.storage.sqlite.connection import open_connection
from omega_stress.infrastructure.storage.sqlite.export_repository import SqliteExportRepository
from omega_stress.infrastructure.storage.sqlite.migrations import apply_schema
from omega_stress.infrastructure.storage.sqlite.profile_repository import SqliteProfileRepository
from omega_stress.infrastructure.storage.sqlite.run_repository import SqliteRunRepository
from omega_stress.infrastructure.storage.sqlite.target_repository import SqliteTargetRepository
from omega_stress.infrastructure.terminal.detector import SystemTerminalDetector
from omega_stress.ports.report_exporter import ReportExporter


@dataclass(frozen=True, slots=True)
class DependencyContainer:
    """Regroupe toutes les instances d'adaptateurs concretes, construites
    une fois au demarrage et partagees pour toute la duree du processus.
    Un dataclass simple plutot qu'un framework DI (coherent avec la
    philosophie "rester leger" du plan produit) : le cablage est
    explicite et lisible dans build_container(), pas magique."""

    connection: sqlite3.Connection
    profile_repository: SqliteProfileRepository
    target_repository: SqliteTargetRepository
    run_repository: SqliteRunRepository
    export_repository: SqliteExportRepository
    settings_store: JsonSettingsStore
    terminal_detector: SystemTerminalDetector
    system_probe: LocalSystemProbe
    load_runner: HttpxLoadGenerator
    audit_logger: AuditLogger
    capability_registry: CapabilityRegistry
    export_dir: Path = field(default_factory=paths.exports_dir)
    screenshot_dir: Path = field(default_factory=paths.screenshots_dir)
    exporters: dict[ExportFormat, ReportExporter] = field(default_factory=dict)


def build_container(*, var_dir: Path | None = None) -> DependencyContainer:
    """Construit et cable l'integralite des adaptateurs concrets. Ouvre
    la connexion SQLite et applique le schema : appeler une seule fois
    par processus."""
    base = var_dir if var_dir is not None else paths.resolve_var_dir()

    connection = open_connection(paths.db_path(base))
    apply_schema(connection)

    return DependencyContainer(
        connection=connection,
        profile_repository=SqliteProfileRepository(connection),
        target_repository=SqliteTargetRepository(connection),
        run_repository=SqliteRunRepository(connection),
        export_repository=SqliteExportRepository(connection),
        settings_store=JsonSettingsStore(paths.settings_path(base)),
        terminal_detector=SystemTerminalDetector(),
        system_probe=LocalSystemProbe(),
        load_runner=HttpxLoadGenerator(),
        audit_logger=AuditLogger(base / "audit.jsonl"),
        capability_registry=CapabilityRegistry(),
        export_dir=paths.exports_dir(base),
        screenshot_dir=paths.screenshots_dir(base),
        exporters={
            ExportFormat.JSON: JsonReportExporter(),
            ExportFormat.CSV: CsvReportExporter(),
            ExportFormat.HTML: HtmlReportExporter(),
        },
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul endroit du projet ou toutes les implementations concretes
#   d'infrastructure/ sont instanciees et cablees ensemble derriere leurs
#   ports respectifs.
# Pourquoi dans app/ (charte) :
# - "assembler... injection de dependances, cablage. Jamais de logique
#   metier" : ce fichier ne decide jamais rien, il construit des objets.
# Ce qu'il ne contient PAS :
# - Aucune regle metier, aucun appel a un command/query de application/.
# - Aucun import direct de sqlite3/httpx/jinja2 : ce fichier importe les
#   CONSTRUCTEURS d'infrastructure/ (SqliteProfileRepository,
#   HttpxLoadGenerator...), jamais les bibliotheques tierces elles-memes
#   — le cablage reste au niveau des objets, pas des APIs bas niveau.
# Points cles :
# - connection est expose comme champ public (pas prive dans un
#   repository) : app/lifecycle.py en a besoin pour fermer proprement la
#   connexion a l'arret, sans que app/ ait a fouiller dans un repository
#   pour la retrouver.
# - exporters: dict[ExportFormat, ReportExporter] est le meme mapping
#   attendu par application/commands/export_run_report.py — construit une
#   seule fois ici, jamais recree a la volee.
# - Aucune capacite n'est pre-enregistree dans capability_registry : le
#   registre est peuple explicitement avant un run Haut/Maximum (depuis
#   system_probe.probe()), pas au demarrage — coherent avec la portee V1
#   du pre-flight check (pas de sondage systematique inutile).
# - export_dir/screenshot_dir (2026-08-24, screenshot_dir le 2026-08-25) :
#   les deux seuls champs de ce dataclass qui ne sont pas des instances
#   d'adaptateur — des Path deja resolus (infrastructure/config/
#   paths.py::exports_dir(base)/screenshots_dir(base), meme `base` que le
#   reste du cablage), exposes pour que interfaces/tui/screens/
#   settings_screen.py, export_dialog.py et app.py puissent proposer un
#   dossier par defaut SANS importer infrastructure/config/paths.py
#   elles-memes (interdit, voir contrat import-linter "interfaces ne
#   dependent jamais directement de infrastructure") — resolus une seule
#   fois ici, comme le reste des chemins runtime, jamais re-derives plus
#   loin.
# Comment il sera utilise (apercu) :
# - app/bootstrap.py appelle build_container() une fois, puis distribue
#   ses champs aux controllers TUI et aux commandes CLI.
#---------------------------------------------------------------------->
