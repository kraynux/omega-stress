# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regles de la charge distribuee (Phase 2, 2026-11-21) : ce qu'un worker accepte, et comment le
debit d'une campagne se repartit entre les workers.

L'autorisation appartient au PROPRIETAIRE du worker (ecrite une fois, sur sa machine) : le
coordinateur ne peut que proposer une campagne dans ce qu'elle permet, jamais la relacher a
distance (plan de charge distribuee §9)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

DISTRIBUTED_PORT = 9650
"""Port TCP du canal de controle (TLS) du coordinateur, par defaut."""


@dataclass(frozen=True, slots=True)
class WorkerAuthorization:
    coordinators: tuple[str, ...]
    """Empreintes SHA-256 (hexadecimal) des certificats de coordinateurs acceptes."""
    targets: tuple[str, ...]
    """Cibles permises : « schema://hote[:port] » (le chemin est libre)."""
    max_requests_per_minute: int
    max_duration_minutes: int
    max_connections: int
    accept_all_targets: bool = False
    """Accord « Tout accepter de mes pilotes » (parc personnel) : toute cible, dans les limites.
    Sinon accord « Demander » : une cible absente de `targets` attend l'accord du proprietaire."""


APPROVAL_NEEDED = "approval needed: "
"""Prefixe de la raison de refus quand seule la cible manque, en accord « Demander » : le pilote
peut alors demander l'accord du proprietaire (parcours simple, 2026-11-21)."""

DEFAULT_MAX_DURATION_MINUTES = 60


def default_limits(cpus: int, sustainable_rps: float | None = None) -> tuple[int, int]:
    """Limites pre-remplies d'une machine qui aide : debit (req/min) et connexions. Debit : celui
    que le calibrage a mesure s'il existe, sinon ~1 000 req/s par coeur, un coeur laisse libre
    (mesure du 2026-11-21) ; connexions : 1 000 par processus d'emission."""
    workers = max(1, cpus - 1)
    rps = sustainable_rps if sustainable_rps and sustainable_rps > 0 else workers * 1000.0
    return int(rps * 60), workers * 1000


def origin_of(url: str) -> str:
    """« https://exemple.org:8443/a?b » -> « https://exemple.org:8443 » ; port par defaut omis."""
    parts = urlsplit(url.strip())
    scheme = (parts.scheme or "http").lower()
    host = (parts.hostname or "").lower()
    default = 443 if scheme == "https" else 80
    port = parts.port if parts.port not in (None, default) else None
    return f"{scheme}://{host}" + (f":{port}" if port else "")


def refusal_reason(
    authorization: WorkerAuthorization | None,
    *,
    coordinator: str,
    target_url: str,
    duration_minutes: float,
    peak_requests_per_minute: float,
    peak_connections: int,
) -> str | None:
    """None si le worker accepte de participer ; sinon la raison (texte court, anglais technique :
    elle voyage dans le protocole et s'affiche cote coordinateur)."""
    if authorization is None:
        return "no worker authorization on this machine (omega-stress worker autoriser)"
    if coordinator not in authorization.coordinators:
        return "coordinator not accepted by this worker"
    if not authorization.accept_all_targets and origin_of(target_url) not in {
        origin_of(t) for t in authorization.targets
    }:
        return f"{APPROVAL_NEEDED}{origin_of(target_url)}"
    if duration_minutes > authorization.max_duration_minutes:
        return f"duration above this worker's limit ({authorization.max_duration_minutes} min)"
    if peak_requests_per_minute > authorization.max_requests_per_minute:
        return f"rate above this worker's limit ({authorization.max_requests_per_minute} req/min)"
    if peak_connections > authorization.max_connections:
        return f"connections above this worker's limit ({authorization.max_connections})"
    return None


def allocate(total: float, capacities: list[float]) -> list[float] | None:
    """Repartition proportionnelle a la capacite de chaque worker (plan §10.2). None si le total
    depasse la somme des capacites : la campagne est refusee et le maximum annonce, jamais
    sous-livree en silence."""
    available = sum(capacities)
    if total > available + 1e-9 or available <= 0:
        return None if total > 0 else [0.0] * len(capacities)
    return [total * capacity / available for capacity in capacities]


def split_whole(total: int, shares: list[float]) -> list[int]:
    """Repartit un nombre entier (connexions) selon des parts, sans en perdre
    (methode des plus grands restes)."""
    if not shares or total <= 0:
        return [0] * len(shares)
    weight = sum(shares) or float(len(shares))
    raw = [total * (share if sum(shares) else 1.0) / weight for share in shares]
    whole = [int(value) for value in raw]
    rest = sorted(range(len(raw)), key=lambda index: raw[index] - whole[index], reverse=True)
    for index in rest[: total - sum(whole)]:
        whole[index] += 1
    return whole
