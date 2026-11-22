# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Fichiers de la charge distribuee sous var/distributed/ (Phase 2, 2026-11-21), en 0600 :

- autorisation.json  (worker) : ce que le PROPRIETAIRE permet (domain/distributed/policies.py) ;
- coordinateurs.json (worker) : coordinateurs appaires -> empreinte, identifiant
  et secret du worker ;
- workers.json       (coordinateur) : workers appaires -> empreinte SHA-256 de leur secret ;
- appairage.json     (coordinateur) : codes a usage unique en attente, avec echeance."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

from omega_stress.domain.distributed.policies import WorkerAuthorization

PAIRING_CODE_SECONDS = 600


class DistributedStore:
    def __init__(self, var_dir: Path) -> None:
        self.directory = var_dir / "distributed"

    # ---- fichiers ----
    def _read(self, name: str, default: Any) -> Any:
        try:
            return json.loads((self.directory / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return default

    def _write(self, name: str, data: Any) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        os.chmod(self.directory, 0o700)
        path = self.directory / name
        tmp = path.with_name(f".{name}.tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

    # ---- autorisation (worker) ----
    def authorization(self) -> WorkerAuthorization | None:
        raw = self._read("autorisation.json", None)
        if not isinstance(raw, dict):
            return None
        try:
            return WorkerAuthorization(
                coordinators=tuple(str(c) for c in raw.get("coordinators", ())),
                targets=tuple(str(t) for t in raw["targets"]),
                max_requests_per_minute=int(raw["max_requests_per_minute"]),
                max_duration_minutes=int(raw["max_duration_minutes"]),
                max_connections=int(raw["max_connections"]),
                accept_all_targets=bool(raw.get("accept_all_targets", False)),
            )
        except (KeyError, TypeError, ValueError):
            return None

    def save_authorization(self, authorization: WorkerAuthorization) -> None:
        self._write(
            "autorisation.json",
            {
                "coordinators": list(authorization.coordinators),
                "targets": list(authorization.targets),
                "max_requests_per_minute": authorization.max_requests_per_minute,
                "max_duration_minutes": authorization.max_duration_minutes,
                "max_connections": authorization.max_connections,
                "accept_all_targets": authorization.accept_all_targets,
            },
        )

    # ---- coordinateurs appaires (worker) ----
    def coordinators(self) -> dict[str, dict[str, str]]:
        """Pilotes appaires, par EMPREINTE (une machine peut joindre le pilote par plusieurs
        adresses : reseau local, VPN) ; chaque fiche garde la derniere adresse connue."""
        raw = self._read("coordinateurs.json", {})
        if not isinstance(raw, dict):
            return {}
        by_fingerprint: dict[str, dict[str, str]] = {}
        for key, record in raw.items():
            if isinstance(record, dict) and "fingerprint" in record:
                # Fiches de la premiere Phase 2 : cle = adresse
                address = str(record.get("address", key if ":" in key else ""))
                by_fingerprint[str(record["fingerprint"])] = {
                    **{k: str(v) for k, v in record.items()}, "address": address
                }
        return by_fingerprint

    def coordinator_for(self, address: str, fingerprint: str | None) -> dict[str, str] | None:
        records = self.coordinators()
        if fingerprint:
            return records.get(fingerprint.lower().replace(":", ""))
        return next((r for r in records.values() if r.get("address") == address), None)

    def save_coordinator(self, address: str, fingerprint: str, worker_id: str, secret: str) -> None:
        data = self.coordinators()
        data[fingerprint] = {
            "fingerprint": fingerprint,
            "address": address,
            "worker_id": worker_id,
            "secret": secret,
        }
        self._write("coordinateurs.json", data)

    def forget_coordinator(self, fingerprint: str) -> bool:
        data = self.coordinators()
        removed = data.pop(fingerprint, None) is not None
        self._write("coordinateurs.json", data)
        authorization = self.authorization()
        if authorization is not None and fingerprint in authorization.coordinators:
            from dataclasses import replace

            self.save_authorization(
                replace(
                    authorization,
                    coordinators=tuple(c for c in authorization.coordinators if c != fingerprint),
                )
            )
        return removed

    def accept_coordinator(self, fingerprint: str) -> None:
        authorization = self.authorization()
        if authorization is not None and fingerprint not in authorization.coordinators:
            from dataclasses import replace

            self.save_authorization(
                replace(authorization, coordinators=(*authorization.coordinators, fingerprint))
            )

    def add_target(self, origin: str) -> bool:
        authorization = self.authorization()
        if authorization is None:
            return False
        if origin not in authorization.targets:
            from dataclasses import replace

            self.save_authorization(
                replace(authorization, targets=(*authorization.targets, origin))
            )
        return True

    # ---- workers appaires (coordinateur) ----
    def workers(self) -> dict[str, dict[str, str]]:
        raw = self._read("workers.json", {})
        return raw if isinstance(raw, dict) else {}

    def add_worker(self, name: str, ssh: str = "", path: str = "") -> tuple[str, str]:
        """Nouvel acces de machine qui aide. ssh (« utilisateur@hote ») et path (dossier
        d'omega-stress
        sur elle) : le pilote la lance lui-meme par SSH a chaque test (parcours simple)."""
        worker_id = secrets.token_hex(8)
        secret = secrets.token_urlsafe(32)
        data = self.workers()
        data[worker_id] = {
            "name": name[:64],
            "secret_sha256": _digest(secret),
            "ssh": ssh,
            "path": path,
        }
        self._write("workers.json", data)
        return worker_id, secret

    def forget_worker(self, worker_id: str) -> bool:
        data = self.workers()
        removed = data.pop(worker_id, None) is not None
        self._write("workers.json", data)
        return removed

    def check_worker(self, worker_id: str, secret: str) -> str | None:
        """Nom du worker si le secret est bon, sinon None (comparaison a temps constant)."""
        entry = self.workers().get(worker_id)
        if not isinstance(entry, dict):
            return None
        if not secrets.compare_digest(entry.get("secret_sha256", ""), _digest(secret)):
            return None
        return str(entry.get("name", worker_id))

    # ---- machines qui participent au prochain test (pilote) ----
    def selection(self) -> dict[str, Any]:
        raw = self._read("selection.json", {})
        return raw if isinstance(raw, dict) else {}

    def save_selection(self, selection: dict[str, Any]) -> None:
        self._write("selection.json", selection)

    # ---- pare-feu (pilote) ----
    def firewall_record(self) -> dict[str, Any]:
        raw = self._read("pare-feu.json", {})
        return raw if isinstance(raw, dict) else {}

    def save_firewall_record(self, record: dict[str, Any]) -> None:
        self._write("pare-feu.json", record)

    # ---- codes d'appairage (coordinateur) ----
    def new_pairing_code(self) -> str:
        code = secrets.token_hex(4).upper()
        now = time.time()
        pending = {c: t for c, t in self._read("appairage.json", {}).items() if t > now}
        pending[_digest(code)] = now + PAIRING_CODE_SECONDS
        self._write("appairage.json", pending)
        return code

    def consume_pairing_code(self, code: str) -> bool:
        pending = self._read("appairage.json", {})
        key = _digest(code.strip().upper())
        valid = isinstance(pending, dict) and pending.get(key, 0) > time.time()
        if isinstance(pending, dict) and key in pending:
            del pending[key]
            self._write("appairage.json", pending)
        return bool(valid)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
