# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ce que l'interface d'omega-stress utilise pour la charge distribuee (lot L3, 2026-11-21) :
machines reliees par omega-connect, leur etat, et le pare-feu de cette machine. Une seule
implementation pour la TUI et la ligne de commande (app/distributed_runner.py).

sudo : `authenticate()` fait `sudo -v` dans le VRAI terminal (l'interface se met de cote pendant ce
temps), puis `firewall_apply()` lance chaque commande en `sudo -n` (jamais d'invite cachee). Jamais
de sudo sans terminal (piege pam_faillock)."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from omega_stress.domain.distributed.policies import DISTRIBUTED_PORT
from omega_stress.infrastructure.distributed import firewall
from omega_stress.infrastructure.distributed.identity import (
    ensure_coordinator_identity,
    fingerprint_of,
)
from omega_stress.infrastructure.distributed.store import DistributedStore

REMOTE_PATH = "export PATH=/usr/local/bin:/usr/bin:/bin:$PATH; "


@dataclass(frozen=True, slots=True)
class HelperMachine:
    machine_id: str
    name: str
    ssh: str
    path: str


@dataclass(frozen=True, slots=True)
class HelperStatus:
    machine: HelperMachine
    reachable: bool
    linked: bool
    """La machine accepte ce pilote (son empreinte est dans son autorisation)."""
    accept_all: bool = False
    max_requests_per_minute: int = 0
    detail: str = ""


class DistributedServices:
    def __init__(self, var_dir: Path) -> None:
        self.store = DistributedStore(var_dir)

    # ---- machines ----
    def machines(self) -> list[HelperMachine]:
        return [
            HelperMachine(
                worker_id,
                str(e.get("name", worker_id)),
                str(e.get("ssh", "")),
                str(e.get("path", "")),
            )
            for worker_id, e in self.store.workers().items()
            if e.get("ssh") and e.get("path")
        ]

    # ---- machines qui participent au prochain test (ecran Charge distribuee) ----
    def participating(self) -> tuple[tuple[str, ...], bool]:
        """(machines cochees, cette machine charge aussi) ; par defaut : toutes les machines
        reliees, cette machine non (decision de l'auteur)."""
        selection = self.store.selection()
        disabled = set(selection.get("disabled", ()))
        ids = tuple(m.machine_id for m in self.machines() if m.machine_id not in disabled)
        return ids, bool(selection.get("local", False))

    def set_participating(self, machine_id: str, participates: bool) -> None:
        selection = self.store.selection()
        disabled = set(selection.get("disabled", ()))
        (disabled.discard if participates else disabled.add)(machine_id)
        self.store.save_selection({**selection, "disabled": sorted(disabled)})

    def set_local(self, participates: bool) -> None:
        self.store.save_selection({**self.store.selection(), "local": participates})

    def remove(self, machine_id: str) -> bool:
        """Retire l'acces de cette machine chez le pilote (omega-connect peut la relier de
        nouveau)."""
        return self.store.forget_worker(machine_id)

    def fingerprint(self) -> str:
        cert, _key = ensure_coordinator_identity(self.store.directory)
        return fingerprint_of(cert)

    def status(self, machine: HelperMachine) -> HelperStatus:
        """Lecture seule par SSH (cle deja acceptee, BatchMode) : `worker etat --format json`."""
        command = (
            REMOTE_PATH
            + f"cd {shlex.quote(machine.path)} && "
            + shlex.join(["./omega-stress.sh", "worker", "etat", "--format", "json"])
        )
        try:
            done = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=8",
                    "--",
                    machine.ssh,
                    command,
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
        except (OSError, subprocess.SubprocessError) as error:
            return HelperStatus(machine, False, False, detail=str(error))
        lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
        if done.returncode != 0 or not lines:
            return HelperStatus(
                machine, False, False, detail=(done.stderr.strip().splitlines() or ["?"])[-1]
            )
        try:
            data = json.loads(lines[-1])
        except ValueError:
            return HelperStatus(machine, True, False, detail="?")
        authorization = data.get("authorization") if isinstance(data, dict) else None
        if not isinstance(authorization, dict):
            return HelperStatus(machine, True, False)
        return HelperStatus(
            machine,
            True,
            self.fingerprint() in authorization.get("coordinators", []),
            bool(authorization.get("accept_all_targets")),
            int(authorization.get("max_requests_per_minute", 0)),
        )

    # ---- pare-feu ----
    def firewall_state(self) -> firewall.FirewallState:
        recorded = self.store.firewall_record()
        backend = firewall.detect_backend()
        networks = firewall.private_networks()
        opened = (
            bool(recorded)
            and recorded.get("backend") == backend
            and set(networks) <= set(recorded.get("networks", ()))
            and recorded.get("port") == DISTRIBUTED_PORT
        )
        return firewall.FirewallState(backend, networks, DISTRIBUTED_PORT, opened)

    def firewall_commands(self, opening: bool) -> tuple[str, tuple[str, ...], list[list[str]]]:
        """(pare-feu, reseaux, commandes) : ouvrir = d'apres cette machine ; fermer = ce qui a ete
        note."""
        state = self.firewall_state()
        if opening:
            backend, networks = state.backend, state.networks
            return backend, networks, firewall.open_commands(backend, networks, DISTRIBUTED_PORT)
        record = self.store.firewall_record()
        backend = str(record.get("backend", state.backend))
        networks = tuple(str(n) for n in record.get("networks", ()))
        return backend, networks, firewall.close_commands(backend, networks, DISTRIBUTED_PORT)

    def note_firewall(
        self,
        opening: bool,
        backend: str,
        networks: tuple[str, ...],
        *,
        by: str = "omega-stress",
        commands: list[list[str]] | None = None,
        outputs: list[str] | None = None,
    ) -> None:
        """Note ce qui a ete fait (compte rendu : qui, quand, quel gestionnaire, quelles regles)."""
        if not opening:
            previous = self.store.firewall_record()
            self.store.save_firewall_record(
                {"closed_at": _now(), "closed_by": by, "previous": previous} if previous else {}
            )
            return
        self.store.save_firewall_record(
            {
                "backend": backend,
                "networks": list(networks),
                "port": DISTRIBUTED_PORT,
                "opened_at": _now(),
                "opened_by": by,
                "rules": firewall.rule_report(backend, commands or [], outputs or []),
            }
        )

    def firewall_record(self) -> dict[str, object]:
        return self.store.firewall_record()

    @staticmethod
    def can_ask_password() -> bool:
        stdin = sys.__stdin__
        return os.geteuid() == 0 or (stdin is not None and stdin.isatty())

    @staticmethod
    def authenticate() -> bool:
        """`sudo -v` dans le vrai terminal (a appeler interface mise de cote)."""
        if os.geteuid() == 0:
            return True
        try:
            return subprocess.run(["sudo", "-v"], check=False).returncode == 0
        except OSError:
            return False

    def firewall_apply(self, opening: bool) -> tuple[bool, str]:
        """Apres authenticate() : chaque commande en sudo -n (aucune invite possible), puis note."""
        backend, networks, commands = self.firewall_commands(opening)
        prefix = [] if os.geteuid() == 0 else ["sudo", "-n"]
        outputs: list[str] = []
        for command in commands:
            try:
                done = subprocess.run(
                    [*prefix, *command],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    check=False,
                    stdin=subprocess.DEVNULL,
                )
            except (OSError, subprocess.SubprocessError) as error:
                return False, str(error)
            if done.returncode != 0:
                return False, (done.stderr.strip().splitlines() or [str(done.returncode)])[-1]
            outputs.append(done.stdout)
        self.note_firewall(opening, backend, networks, commands=commands, outputs=outputs)
        return True, ""


def _now() -> str:
    from datetime import datetime

    return datetime.now().astimezone().isoformat(timespec="seconds")
