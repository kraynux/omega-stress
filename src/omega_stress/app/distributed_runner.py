# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Commandes de la charge distribuee (Phase 2 + parcours simple, 2026-11-21), sans interface.

Parcours simple : omega-connect relie les machines a la place de l'utilisateur, avec ces commandes
(sorties `--format json`, jamais traduites) ; l'utilisateur n'en tape aucune.

  Pilote :
    coordinateur etat [--format json]               empreinte, machines qui aident, pare-feu
    coordinateur ajouter-machine --nom N --ssh U@H --chemin DOSSIER [--format json]
                                                    acces d'une machine qui aide (secret affiche
                                                    une seule fois, a transmettre par SSH)
    coordinateur retirer-machine ID
    coordinateur pare-feu etat|ouvrir|fermer [--format json] [--commandes] [--fait]
    coordinateur code | appairage                   appairage par code (ligne de commande)
  Machine qui aide :
    worker relier --pilote-adresse H:P --pilote-empreinte E --id ID [--accord demander|tout]
                                                    (secret lu sur l'entree standard)
    worker autoriser [--cible URL…] [--accord demander|tout] [--debit-max N] [--duree-max M]
                     [--connexions-max C] | --ajouter-cible URL
    worker retirer-pilote EMPREINTE
    worker appairer H:P --empreinte E --code C      appairage par code (ligne de commande)
    worker rejoindre H:P [--pilote EMPREINTE] [--une-fois]
    worker etat [--format json]

Le test distribue part de `run request|connection|ramp … --machines ID,ID [--cette-machine]`
(ou `--distribue N` pour des machines qui rejoignent d'elles-memes)."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import socket
import sys
from dataclasses import replace
from pathlib import Path

from omega_stress.domain.distributed.policies import (
    DEFAULT_MAX_DURATION_MINUTES,
    DISTRIBUTED_PORT,
    WorkerAuthorization,
    default_limits,
    origin_of,
)
from omega_stress.infrastructure.config import paths
from omega_stress.infrastructure.distributed import firewall, worker_agent
from omega_stress.infrastructure.distributed.coordinator import Coordinator
from omega_stress.infrastructure.distributed.services import DistributedServices
from omega_stress.infrastructure.distributed.store import PAIRING_CODE_SECONDS, DistributedStore

ACCORDS = ("demander", "tout")


def _store(var_dir: Path | None) -> DistributedStore:
    return DistributedStore(var_dir if var_dir is not None else paths.resolve_var_dir())


def _say(text: str) -> None:
    print(text, flush=True)


def _json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False), flush=True)


def _firewall_state(store: DistributedStore, port: int) -> firewall.FirewallState:
    services = DistributedServices(store.directory.parent)
    return services.firewall_state()


def _sustainable_rps(var_dir: Path | None) -> float | None:
    """Debit sur (enveloppe `rps_safe`) du dernier calibrage de cette machine, s'il existe."""
    base = var_dir if var_dir is not None else paths.resolve_var_dir()
    try:
        files = sorted(paths.calibrations_dir(base).glob("*.json"), key=lambda p: p.stat().st_mtime)
        data = json.loads(files[-1].read_text(encoding="utf-8")) if files else {}
    except (OSError, ValueError, IndexError):
        return None
    if not isinstance(data, dict):
        return None
    envelope = data.get("envelope")
    value = envelope.get("rps_safe") if isinstance(envelope, dict) else None
    return float(value) if isinstance(value, (int, float)) and value > 0 else None


# ------------------------------------------------------------------ pilote
def run_coordinator(argv: list[str], *, var_dir: Path | None = None) -> int:
    parser = argparse.ArgumentParser(prog="omega-stress coordinateur")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("code", help="Code d'appairage a usage unique (10 min)").add_argument(
        "--format", choices=("texte", "json"), default="texte"
    )
    sub.add_parser("etat", help="Empreinte, machines qui aident, pare-feu").add_argument(
        "--format", choices=("texte", "json"), default="texte"
    )
    add = sub.add_parser("ajouter-machine", help="Acces d'une machine qui aide (omega-connect)")
    add.add_argument("--nom", required=True)
    add.add_argument("--ssh", required=True, help="utilisateur@hote")
    add.add_argument("--chemin", required=True, help="dossier d'omega-stress sur cette machine")
    add.add_argument("--format", choices=("texte", "json"), default="texte")
    remove = sub.add_parser("retirer-machine")
    remove.add_argument("machine_id")
    wall = sub.add_parser("pare-feu", help="Port d'omega-stress pour le reseau local")
    wall.add_argument("operation", choices=("etat", "ouvrir", "fermer"))
    wall.add_argument("--format", choices=("texte", "json"), default="texte")
    wall.add_argument(
        "--commandes",
        action="store_true",
        help="Donne les commandes (a lancer en root par l'appelant) sans les lancer",
    )
    wall.add_argument(
        "--fait", action="store_true", help="Note que l'appelant a lance les commandes avec succes"
    )
    wall.add_argument(
        "--par", default="omega-stress", help="Qui a lance les commandes (compte rendu)"
    )
    listen = sub.add_parser("appairage", help="Ecoute le temps d'appairer des machines")
    listen.add_argument("--port", type=int, default=DISTRIBUTED_PORT)
    listen.add_argument("--minutes", type=float, default=PAIRING_CODE_SECONDS / 60)
    args = parser.parse_args(argv)
    store = _store(var_dir)

    if args.action == "code":
        code = store.new_pairing_code()
        fingerprint = Coordinator(store, DISTRIBUTED_PORT).fingerprint
        if args.format == "json":
            _json({"code": code, "fingerprint": fingerprint, "port": DISTRIBUTED_PORT})
            return 0
        _say(f"Code d'appairage : {code} (valable {PAIRING_CODE_SECONDS // 60} min, une fois)")
        _say(f"Empreinte du coordinateur : {fingerprint}")
        _say(
            "Sur le worker : omega-stress.sh worker appairer <cette machine>:<port> "
            f"--empreinte {fingerprint} --code {code}"
        )
        return 0
    if args.action == "etat":
        fingerprint = Coordinator(store, DISTRIBUTED_PORT).fingerprint
        machines = [
            {
                "id": worker_id,
                "name": e.get("name", ""),
                "ssh": e.get("ssh", ""),
                "path": e.get("path", ""),
            }
            for worker_id, e in store.workers().items()
        ]
        wall_state = _firewall_state(store, DISTRIBUTED_PORT)
        if args.format == "json":
            _json(
                {
                    "fingerprint": fingerprint,
                    "port": DISTRIBUTED_PORT,
                    "host": socket.gethostname(),
                    "machines": machines,
                    "firewall": wall_state.to_dict(),
                }
            )
            return 0
        _say(f"Empreinte du coordinateur : {fingerprint}")
        _say(f"Machines qui aident : {len(machines)}")
        for machine in machines:
            _say(f"  {machine['name']}  ({machine['id']}) {machine['ssh']}")
        _say(
            f"Pare-feu : {wall_state.backend}"
            + (" — port fermé aux machines qui aident" if wall_state.needs_opening else "")
        )
        return 0
    if args.action == "ajouter-machine":
        fingerprint = Coordinator(store, DISTRIBUTED_PORT).fingerprint
        worker_id, secret = store.add_worker(args.nom, ssh=args.ssh, path=args.chemin)
        if args.format == "json":
            _json(
                {
                    "id": worker_id,
                    "secret": secret,
                    "fingerprint": fingerprint,
                    "port": DISTRIBUTED_PORT,
                }
            )
        else:
            _say(f"Machine ajoutée : {args.nom} ({worker_id})")
            _say(f"Secret (à transmettre une seule fois, par SSH) : {secret}")
        return 0
    if args.action == "retirer-machine":
        return 0 if store.forget_worker(args.machine_id) else 1
    if args.action == "pare-feu":
        return _run_firewall(store, args)
    return asyncio.run(_listen_for_pairing(store, args.port, args.minutes))


def _run_firewall(store: DistributedStore, args: argparse.Namespace) -> int:
    services = DistributedServices(store.directory.parent)
    state = services.firewall_state()
    if args.operation == "etat":
        if args.format == "json":
            _json({**state.to_dict(), "record": services.firewall_record()})
        else:
            _say(
                f"Pare-feu : {state.backend} ; réseaux : {', '.join(state.networks) or '-'} ; "
                + (
                    "port ouvert par omega-stress"
                    if state.opened
                    else "port à ouvrir"
                    if state.needs_opening
                    else "rien à ouvrir"
                )
            )
        return 0
    opening = args.operation == "ouvrir"
    backend, networks, commands = services.firewall_commands(opening)
    if opening and not commands and state.needs_omega_fire:
        _say(
            "Pare-feu : nftables seul — omega-fire est nécessaire pour ouvrir le port "
            "(omega-stress ne réécrit jamais la configuration nftables)."
        )
        return 1
    if args.commandes:
        _json({"backend": backend, "commands": commands})
        return 0
    if args.fait or not commands:
        # omega-connect a lance les commandes dans sa propre invite sudo : il transmet ce
        # qu'elles ont repondu (JSON sur l'entree standard) pour le compte rendu (regles,
        # numeros omega-fire).
        outputs: list[str] = []
        if args.fait and not sys.stdin.isatty():
            try:
                data = json.loads(sys.stdin.read() or "{}")
                outputs = (
                    [str(o) for o in data.get("outputs", [])] if isinstance(data, dict) else []
                )
            except (OSError, ValueError):
                outputs = []
        if commands:
            services.note_firewall(
                opening, backend, networks, by=args.par, commands=commands, outputs=outputs
            )
        return 0
    if not sys.stdin.isatty():
        # Jamais de sudo sans terminal : des echecs « conversation failed » verrouillent le compte
        # (pam_faillock). omega-connect et la TUI passent par --commandes et leur propre invite.
        _say("Pare-feu : un terminal est nécessaire pour le mot de passe (sudo).")
        return 1
    if not services.authenticate():
        _say("Pare-feu : mot de passe refusé, rien n'est modifié.")
        return 1
    ok, detail = services.firewall_apply(opening)
    if not ok:
        _say(f"Pare-feu : commande refusée ({detail}), rien n'est noté.")
        return 1
    _say("Pare-feu : port d'omega-stress " + ("ouvert au réseau local." if opening else "refermé."))
    return 0


async def _listen_for_pairing(store: DistributedStore, port: int, minutes: float) -> int:
    coordinator = Coordinator(store, port)
    await coordinator.start()
    _say(
        f"Coordinateur à l'écoute pour l'appairage (port {coordinator.port}, {minutes:g} min) ; "
        "Ctrl+C pour arrêter."
    )
    seen = 0
    try:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + minutes * 60
        while loop.time() < deadline:
            await coordinator.wait_for(
                lambda known=seen: len(coordinator.paired) > known,  # type: ignore[misc]
                deadline - loop.time(),
            )
            for name in coordinator.paired[seen:]:
                _say(f"Worker appairé : {name}")
            seen = len(coordinator.paired)
    finally:
        await coordinator.stop()
    return 0


# ------------------------------------------------------------------ machine qui aide
def _authorization_with(
    store: DistributedStore,
    var_dir: Path | None,
    *,
    accord: str | None,
    targets: tuple[str, ...] = (),
    rpm: int | None = None,
    minutes: int | None = None,
    connections: int | None = None,
) -> WorkerAuthorization:
    """Autorisation mise a jour ; limites absentes = pre-remplies d'apres cette machine."""
    previous = store.authorization()
    auto_rpm, auto_connections = default_limits(os.cpu_count() or 1, _sustainable_rps(var_dir))
    base = previous or WorkerAuthorization(
        coordinators=tuple(store.coordinators()),
        targets=(),
        max_requests_per_minute=auto_rpm,
        max_duration_minutes=DEFAULT_MAX_DURATION_MINUTES,
        max_connections=auto_connections,
        accept_all_targets=False,
    )
    return replace(
        base,
        targets=tuple(dict.fromkeys((*base.targets, *(origin_of(t) for t in targets)))),
        max_requests_per_minute=rpm or base.max_requests_per_minute,
        max_duration_minutes=minutes or base.max_duration_minutes,
        max_connections=connections or base.max_connections,
        accept_all_targets=(accord == "tout") if accord else base.accept_all_targets,
    )


def run_worker(argv: list[str], *, var_dir: Path | None = None, version: str = "") -> int:
    parser = argparse.ArgumentParser(prog="omega-stress worker")
    sub = parser.add_subparsers(dest="action", required=True)
    allow = sub.add_parser("autoriser", help="Autorisation du proprietaire de cette machine")
    allow.add_argument("--cible", action="append", default=[], help="URL permise (repetable)")
    allow.add_argument("--ajouter-cible", default=None, help="Ajoute une cible (accord donne)")
    allow.add_argument("--accord", choices=ACCORDS, default=None)
    allow.add_argument("--debit-max", type=int, default=None, help="req/min au plus")
    allow.add_argument("--duree-max", type=int, default=None, help="minutes au plus")
    allow.add_argument("--connexions-max", type=int, default=None)
    link = sub.add_parser("relier", help="Relie cette machine a un pilote (omega-connect)")
    link.add_argument("--pilote-adresse", required=True)
    link.add_argument("--pilote-empreinte", required=True)
    link.add_argument("--id", required=True)
    link.add_argument("--accord", choices=ACCORDS, default="demander")
    unlink = sub.add_parser("retirer-pilote")
    unlink.add_argument("empreinte")
    pair = sub.add_parser("appairer", help="Appairage avec un coordinateur (code)")
    pair.add_argument("adresse")
    pair.add_argument("--empreinte", required=True)
    pair.add_argument("--code", required=True)
    join = sub.add_parser("rejoindre", help="Rejoint le coordinateur et sert ses campagnes")
    join.add_argument("adresse")
    join.add_argument("--pilote", default=None, help="Empreinte du pilote attendu")
    join.add_argument("--une-fois", action="store_true", help="S'arreter apres une campagne")
    sub.add_parser("etat", help="Autorisation et pilotes").add_argument(
        "--format", choices=("texte", "json"), default="texte"
    )
    args = parser.parse_args(argv)
    store = _store(var_dir)

    if args.action == "autoriser":
        if args.ajouter_cible:
            if not store.add_target(origin_of(args.ajouter_cible)):
                _say("Aucune autorisation sur cette machine.")
                return 1
            return 0
        limits = (args.debit_max, args.duree_max, args.connexions_max)
        if any(value is not None and value <= 0 for value in limits):
            _say("Les limites doivent être positives.")
            return 2
        store.save_authorization(
            _authorization_with(
                store,
                var_dir,
                accord=args.accord,
                targets=tuple(args.cible),
                rpm=args.debit_max,
                minutes=args.duree_max,
                connections=args.connexions_max,
            )
        )
        _say("Autorisation enregistrée (var/distributed/autorisation.json).")
        return 0
    if args.action == "relier":
        secret = sys.stdin.readline().strip()
        if not secret:
            _say("Secret absent (attendu sur l'entrée standard).")
            return 2
        fingerprint = args.pilote_empreinte.lower().replace(":", "")
        store.save_coordinator(args.pilote_adresse, fingerprint, args.id, secret)
        store.save_authorization(_authorization_with(store, var_dir, accord=args.accord))
        store.accept_coordinator(fingerprint)
        return 0
    if args.action == "retirer-pilote":
        return 0 if store.forget_coordinator(args.empreinte.lower().replace(":", "")) else 1
    if args.action == "appairer":
        try:
            fingerprint = asyncio.run(
                worker_agent.pair(store, args.adresse, args.empreinte, args.code)
            )
        except (OSError, ValueError, asyncio.TimeoutError, RuntimeError) as error:
            _say(f"Appairage refusé : {error}")
            return 1
        _say(f"Appairé avec {args.adresse} (empreinte {fingerprint[:16]}…).")
        if store.authorization() is None:
            _say("Aucune autorisation sur cette machine : omega-stress.sh worker autoriser …")
        return 0
    if args.action == "rejoindre":
        # Sans --une-fois, la machine reste disponible : le pilote n'ecoute que pendant un test
        # distribue, elle se remet donc en attente du suivant apres chaque test.
        while True:
            try:
                code = asyncio.run(
                    worker_agent.join(
                        store,
                        args.adresse,
                        version=version,
                        once=args.une_fois,
                        log=_say,
                        fingerprint=args.pilote,
                    )
                )
            except (OSError, ValueError, asyncio.TimeoutError) as error:
                _say(f"Coordinateur injoignable : {error}")
                return 1
            except KeyboardInterrupt:
                return 0
            if args.une_fois or code != 0:
                return code
    return _worker_state(store, args.format)


def _worker_state(store: DistributedStore, output: str) -> int:
    authorization = store.authorization()
    if output == "json":
        _json(
            {
                "host": socket.gethostname(),
                "authorization": None
                if authorization is None
                else {
                    "targets": list(authorization.targets),
                    "accept_all_targets": authorization.accept_all_targets,
                    "max_requests_per_minute": authorization.max_requests_per_minute,
                    "max_duration_minutes": authorization.max_duration_minutes,
                    "max_connections": authorization.max_connections,
                    "coordinators": list(authorization.coordinators),
                },
                "coordinators": [
                    {"fingerprint": f, "address": r.get("address", "")}
                    for f, r in store.coordinators().items()
                ],
            }
        )
        return 0
    if authorization is None:
        _say("Autorisation : aucune (ce worker refuse toute campagne).")
    else:
        _say(
            "Accord : "
            + (
                "tout accepter de mes pilotes"
                if authorization.accept_all_targets
                else "demander pour chaque nouvelle cible"
            )
        )
        _say(f"Cibles permises : {', '.join(authorization.targets) or '-'}")
        _say(
            f"Débit max : {authorization.max_requests_per_minute} req/min ; durée max : "
            f"{authorization.max_duration_minutes} min ; connexions max : "
            f"{authorization.max_connections}"
        )
        _say(f"Coordinateurs acceptés : {len(authorization.coordinators)}")
    for fingerprint, record in store.coordinators().items():
        _say(f"Appairé : {record.get('address', '?')} ({fingerprint[:16]}…)")
    return 0


def main(argv: list[str]) -> int:
    from omega_stress.core.constants import OMEGA_STRESS_VERSION

    if argv[:1] == ["coordinateur"]:
        return run_coordinator(argv[1:])
    if argv[:1] == ["worker"]:
        return run_worker(argv[1:], version=OMEGA_STRESS_VERSION)
    print("usage: omega-stress worker|coordinateur …", file=sys.stderr)
    return 2
