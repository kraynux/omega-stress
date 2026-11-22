# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Pare-feu du pilote (parcours simple, 2026-11-21) : les machines qui aident doivent joindre le
port d'omega-stress. Ouverture limitee aux reseaux prives de cette machine (reseau local, VPN) et
au seul port d'omega-stress.

Ordre (decision de l'auteur, 2026-11-21) : omega-fire s'il est relie par omega-connect
(`omega-fire.sh port ouvrir|fermer` : nftables, iptables, et ufw/firewalld s'ils sont actifs,
journal d'audit) ; sinon ufw ou firewalld directement ; nftables seul sans omega-fire : rien
n'est modifie a la main, omega-fire est propose (la configuration nftables de l'utilisateur n'est
jamais reecrite).

Les commandes sont DONNEES (jamais lancees en root par ce module) et demandent root : l'appelant
fait `sudo -v` dans un VRAI terminal (mot de passe tape une fois), puis `sudo -n` pour chaque
commande ; jamais de sudo sans terminal (piege pam_faillock : des echecs « conversation failed »
verrouillent le compte). Ce qui a ete ouvert est note dans var/distributed/pare-feu.json pour le
refermer exactement."""

from __future__ import annotations

import ipaddress
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

NONE, UFW, FIREWALLD, OTHER = "aucun", "ufw", "firewalld", "nftables"
OMEGA_FIRE = "omega-fire"
LABEL = "omega-stress"
_PRIVATE = [
    ipaddress.IPv4Network(n)
    for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10")
]


@dataclass(frozen=True, slots=True)
class FirewallState:
    backend: str
    networks: tuple[str, ...]
    port: int
    opened: bool
    """Regle d'omega-stress notee comme ouverte (var/distributed/pare-feu.json)."""

    @property
    def needs_opening(self) -> bool:
        return self.backend in (UFW, FIREWALLD, OMEGA_FIRE) and not self.opened

    @property
    def needs_omega_fire(self) -> bool:
        """nftables seul, sans omega-fire : le port ne peut pas etre ouvert sans lui."""
        return self.backend == OTHER and not self.opened

    def to_dict(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "networks": list(self.networks),
            "port": self.port,
            "opened": self.opened,
            "needs_opening": self.needs_opening,
            "needs_omega_fire": self.needs_omega_fire,
        }


def _active(unit: str) -> bool:
    try:
        result = subprocess.run(
            ["systemctl", "is-active", unit], capture_output=True, text=True, timeout=5, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.stdout.strip() == "active"


def omega_fire_launcher() -> str:
    """Lanceur d'omega-fire s'il est relie par omega-connect (registre de l'espace partage actif),
    comme
    omega-serv pour son administration web ; « » sinon. Jamais d'exception."""
    try:
        from omega_lib.infrastructure.synchro.files import read_contract, zone_dir
        from omega_lib.synchro.constants import TOOL_LAUNCHERS, ZONE_REGISTRY
        from omega_lib.synchro.registry import ZoneState, registry_from_dict

        registry = read_contract(zone_dir() / ZONE_REGISTRY, registry_from_dict).value
        if registry is None or registry.state is not ZoneState.ACTIVE:
            return ""
        fire = next((e for e in registry.installations if e.tool == "omega-fire"), None)
        if fire is None:
            return ""
        launcher = Path(fire.root) / TOOL_LAUNCHERS["omega-fire"]
        return str(launcher) if launcher.is_file() and not launcher.is_symlink() else ""
    except Exception:  # noqa: BLE001 - omega-lib ancien ou registre illisible : pas d'omega-fire
        return ""


def detect_backend() -> str:
    if omega_fire_launcher():
        return OMEGA_FIRE
    if _active("ufw"):
        return UFW
    if _active("firewalld"):
        return FIREWALLD
    if _active("nftables"):
        return OTHER
    return NONE


def private_networks() -> tuple[str, ...]:
    """Reseaux prives de cette machine (adresses IPv4 des interfaces), ex. 192.168.1.0/24."""
    try:
        raw = subprocess.run(
            ["ip", "-j", "-4", "addr"], capture_output=True, text=True, timeout=5, check=False
        ).stdout
        interfaces = json.loads(raw or "[]")
    except (OSError, subprocess.SubprocessError, ValueError):
        return ()
    found: list[str] = []
    for interface in interfaces:
        for info in interface.get("addr_info", []):
            try:
                network = ipaddress.IPv4Interface(f"{info['local']}/{info['prefixlen']}").network
            except (KeyError, ValueError):
                continue
            if network.prefixlen == 32 and network.subnet_of(_PRIVATE[3]):
                # Tailscale et autres VPN « point a point » (adresse /32) : les autres machines
                # du reseau prive sont dans tout le bloc 100.64.0.0/10.
                network = _PRIVATE[3]
            if any(network.subnet_of(p) for p in _PRIVATE) and str(network) not in found:
                found.append(str(network))
    return tuple(found)


def _omega_fire(operation: str, networks: tuple[str, ...], port: int) -> list[list[str]]:
    launcher = omega_fire_launcher()
    if not launcher or not networks:
        return []
    return [
        [
            launcher,
            "port",
            operation,
            "--port",
            str(port),
            "--sources",
            ",".join(networks),
            "--pour",
            LABEL,
            "--format",
            "json",
        ]
    ]


def open_commands(backend: str, networks: tuple[str, ...], port: int) -> list[list[str]]:
    if backend == OMEGA_FIRE:
        return _omega_fire("ouvrir", networks, port)
    if backend == UFW:
        return [
            [
                "ufw",
                "allow",
                "from",
                n,
                "to",
                "any",
                "port",
                str(port),
                "proto",
                "tcp",
                "comment",
                "omega-stress",
            ]
            for n in networks
        ]
    if backend == FIREWALLD:
        return [
            ["firewall-cmd", "--permanent", f"--add-rich-rule={_rich_rule(n, port)}"]
            for n in networks
        ] + [["firewall-cmd", "--reload"]]
    return []


def close_commands(backend: str, networks: tuple[str, ...], port: int) -> list[list[str]]:
    if backend == OMEGA_FIRE:
        return _omega_fire("fermer", networks, port)
    if backend == UFW:
        return [
            ["ufw", "delete", "allow", "from", n, "to", "any", "port", str(port), "proto", "tcp"]
            for n in networks
        ]
    if backend == FIREWALLD:
        return [
            ["firewall-cmd", "--permanent", f"--remove-rich-rule={_rich_rule(n, port)}"]
            for n in networks
        ] + [["firewall-cmd", "--reload"]]
    return []


def _rich_rule(network: str, port: int) -> str:
    return f'rule family="ipv4" source address="{network}" port port="{port}" protocol="tcp" accept'


def rule_report(
    backend: str, commands: list[list[str]], outputs: list[str]
) -> list[dict[str, str]]:
    """Regles posees, pour le compte rendu (retour de l'auteur, 2026-11-21 : « qui a ouvert le
    port, quelle regle, quel pare-feu ») : omega-fire rend une ligne par gestionnaire et par
    reseau (nftables, iptables, ufw, firewalld ; etat ; numero de regle) ; ufw et firewalld : la
    commande lancee."""
    lines: list[dict[str, str]] = []
    if backend == OMEGA_FIRE:
        for output in outputs:
            for raw in reversed(output.splitlines()):
                if raw.strip().startswith("{"):
                    try:
                        data = json.loads(raw)
                    except ValueError:
                        break
                    for line in data.get("lignes", []) if isinstance(data, dict) else []:
                        if isinstance(line, dict):
                            lines.append(
                                {
                                    "manager": str(line.get("cible", "")),
                                    "network": str(line.get("source", "")),
                                    "state": str(line.get("etat", "")),
                                    "rule": str(line.get("detail", "")),
                                }
                            )
                    break
        return lines
    for command in commands:
        network = next((part for part in command if "/" in part and part[0].isdigit()), "")
        if not network and "--add-rich-rule" in " ".join(command):
            network = command[-1].split('address="', 1)[-1].split('"', 1)[0]
        if command[:1] == ["firewall-cmd"] and "--reload" in command:
            continue
        lines.append(
            {"manager": backend, "network": network, "state": "ajoutee", "rule": " ".join(command)}
        )
    return lines
