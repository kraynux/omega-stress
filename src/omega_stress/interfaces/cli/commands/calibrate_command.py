# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sous-commande CLI `calibrate` : calibrage local persistant (mesure de
la capacite reelle de la machine hote, jamais de la cible testee)."""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from typing import TYPE_CHECKING

from omega_stress.application.commands.run_calibration import run_calibration
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.calibration.models import CalibrationResult
from omega_stress.domain.calibration.service import compute_fingerprint_hash
from omega_stress.shared.clock import utc_now

if TYPE_CHECKING:
    # Import reserve au typage statique (voir interfaces/cli/commands/
    # run_command.py pour la justification complete) : jamais execute a
    # l'import reel.
    from omega_stress.app.dependency_container import DependencyContainer


def register(subparsers: argparse._SubParsersAction) -> None:
    """Enregistre `calibrate run|show` sur le parser CLI."""
    parser = subparsers.add_parser(
        "calibrate", help="Calibrage local persistant de cette machine"
    )
    actions = parser.add_subparsers(dest="calibrate_action", required=True)

    run_parser = actions.add_parser("run", help="Lancer un nouveau calibrage")
    run_parser.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    run_parser.set_defaults(handler=_handle_run)

    show_parser = actions.add_parser("show", help="Afficher le dernier calibrage connu")
    show_parser.add_argument(
        "--json", action="store_true", help="Sortie machine (JSON) plutot que texte humain"
    )
    show_parser.set_defaults(handler=_handle_show)


class _CliStageProgressNotifier:
    """Notifier minimal pour le mode CLI : ligne de progression compacte
    sur stderr, mise a jour sur place (\\r) — meme convention que
    _CliProgressNotifier de run_command.py. Bug reel corrige le
    2026-09-02 (voir ports/calibration_stage_progress_notifier.py) :
    avant ce notifier, aucun signal n'existait entre deux paliers,
    indiscernable d'un blocage si un palier prenait plus de temps que
    prevu."""

    def notify(self, stage_id: str, elapsed_seconds: int, window_seconds: int) -> None:
        sys.stderr.write(f"\r[{stage_id}] {elapsed_seconds}s/{window_seconds}s   ")
        sys.stderr.flush()


async def _handle_run(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    outcome = await run_calibration(
        compute_fingerprint=container.compute_calibration_fingerprint,
        preconditions_probe=container.calibration_preconditions_probe,
        server_factory=container.calibration_server_factory,
        stage_runner_factory=container.calibration_stage_runner_factory,
        calibration_repository=container.calibration_repository,
        now=utc_now,
        notification_sink=_print_notification,
        stage_progress_notifier=_CliStageProgressNotifier(),
    )
    sys.stderr.write("\n")
    if isinstance(outcome, Err):
        return Err(str(outcome.error))
    return Ok(_format(outcome.value, as_json=args.json))


async def _handle_show(
    args: argparse.Namespace, container: DependencyContainer
) -> Result[str, str]:
    fingerprint_hash = compute_fingerprint_hash(container.compute_calibration_fingerprint())
    result = container.calibration_repository.load(fingerprint_hash)
    if result is None:
        return Err("Aucun calibrage connu pour cette machine.")
    return Ok(_format(result, as_json=args.json))


def _format(result: CalibrationResult, *, as_json: bool) -> str:
    if as_json:
        payload = dataclasses.asdict(result)
        payload["started_at"] = result.started_at.isoformat()
        return json.dumps(payload, indent=2, ensure_ascii=False)
    if result.envelope is None:
        reason = result.overall_stop_reason or "echec precoce"
        return f"Aucune enveloppe exploitable ({reason})."
    envelope = result.envelope
    return (
        f"VU_safe={envelope.vu_safe} RPS_safe={envelope.rps_safe} "
        f"confiance={envelope.confidence} "
        f"dernier_palier_sain={envelope.last_healthy_stage_id}"
    )


def _print_notification(message: str) -> None:
    print(message, file=sys.stderr)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit `omega-stress calibrate run|show` en appel a
#   application/commands/run_calibration.py, ou en simple lecture du
#   dernier resultat persiste.
# Pourquoi dans interfaces/cli/commands/ (charte) :
# - Adaptateur de presentation scriptable, symetrique a
#   interfaces/tui/controllers/calibration_controller.py pour le TUI.
# Ce qu'il ne contient PAS :
# - Aucun import de interfaces/tui/ (CLI et TUI restent deux adaptateurs
#   independants par choix produit, ARCHITECTURE.md §0 — meme raison
#   documentee dans interfaces/tui/controllers/load_controller.py) :
#   l'appel a run_calibration() est duplique ici plutot que de reutiliser
#   calibration_controller.py, exactement comme run_command.py duplique
#   deja _ensure_capabilities_probed() plutot que d'importer
#   load_controller.py.
# - Aucun _finish() dedie (contrairement a run_command.py, qui en a besoin
#   pour choisir entre to_json()/format_run() sur un RunDTO) : chaque
#   handler ici construit deja directement son Result[str, str] via
#   _format(), main.py::run() se charge du format_error() final sur un
#   Err quel qu'il soit — meme point unique de formatage d'erreur que les
#   quatre autres modules de commands/.
# Points cles :
# - `calibrate run` VS `calibrate show` : run() declenche un nouveau
#   calibrage (potentiellement plusieurs minutes, notifications par
#   palier sur stderr comme _CliProgressNotifier de run_command.py, plus
#   une ligne de progression PAR SECONDE via _CliStageProgressNotifier,
#   2026-09-02, meme bug reel corrige cote TUI) ;
#   show() relit seulement le dernier resultat deja persiste
#   (CalibrationRepository.load(), instantane, jamais de mesure reelle) —
#   deux sous-commandes distinctes plutot qu'un seul `calibrate --show`,
#   symetrique a `run precheck|request|connection|ramp|replay`.
# - _format() : CalibrationResult est un type domain/ (pas un DTO, voir
#   application/commands/run_calibration.py, INFO DEV) — dataclasses.
#   asdict() suffit (tous ses champs imbriques sont des dataclasses
#   simples sans SystemSnapshot, voir domain/calibration/models.py), seul
#   started_at (datetime) exige une conversion manuelle en isoformat avant
#   json.dumps(), contrairement a text_formatter.py::to_json() (generique,
#   mais suppose des DTO deja stringifies) qui n'est donc pas reutilise
#   ici.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py appelle register() au demarrage.
#---------------------------------------------------------------------->
