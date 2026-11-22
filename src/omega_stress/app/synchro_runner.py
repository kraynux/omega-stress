# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""`omega-stress.sh synchro jeton [--format json]` (contrats d'interconnexion, 2026-11-21) : carte
d'identite lue par omega-connect, sans interface ni bannière, sortie JSON non traduite. Meme format
que les autres outils omega (omega_lib.infrastructure.synchro.install_token) : jamais ecrit en root,
seul le proprietaire du dossier l'ecrit, `var/omega-jeton.json`, exclu de l'archive.

omega-stress n'a pas encore de fiche : ses capacites (`distributed-worker`, `native-generator`)
seront declarees quand la charge distribuee existera (plan
STRESS/plan-omega-stress-charge-distribué.md, phase 2)."""

from __future__ import annotations

import sys
from pathlib import Path

STRESS_TOOL = "omega-stress"
USAGE = "usage: omega-stress.sh synchro jeton [--format json]"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_synchro(argv: list[str]) -> int:
    from omega_lib.infrastructure.declaration.app_version import project_version
    from omega_lib.infrastructure.synchro.files import dumps
    from omega_lib.infrastructure.synchro.install_token import refresh_install_token
    from omega_lib.synchro.codec import token_to_dict

    args = list(argv)
    if args[-2:] == ["--format", "json"]:
        args = args[:-2]
    if args != ["jeton"]:
        print(USAGE, file=sys.stderr)
        return 2
    root = project_root()
    refresh = refresh_install_token(root, STRESS_TOOL, project_version(root, STRESS_TOOL))
    if refresh.token is None:
        print(
            f"omega-stress: installation token not written ({refresh.path}): {refresh.reason}",
            file=sys.stderr,
        )
        return 1
    print(dumps(token_to_dict(refresh.token)), end="")
    return 0
