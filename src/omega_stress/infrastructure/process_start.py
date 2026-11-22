# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Demarrer un processus multiprocessing depuis l'interface (correctif 2.0.0, 2026-11-21).

Sous Textual, sys.stdout / sys.stderr sont remplaces par des objets de capture dont le descripteur
vaut -1. multiprocessing (spawn) transmet le descripteur de sys.stderr au suivi des ressources du
processus enfant : avec -1, le lancement echoue (« ValueError: bad value(s) in fds_to_keep »), et
aucun test ne partait depuis l'interface (la ligne de commande, elle, marchait). Pendant le seul
`start()`, les vrais flux du processus sont remis en place."""

from __future__ import annotations

import contextlib
import os
import sys
from collections.abc import Iterator
from typing import Any


def _usable(stream: Any) -> bool:
    try:
        return stream is not None and stream.fileno() >= 0
    except (AttributeError, OSError, ValueError):
        return False


@contextlib.contextmanager
def real_stdio() -> Iterator[None]:
    saved = sys.stdout, sys.stderr
    spare = None
    try:
        for name, original in (("stdout", sys.__stdout__), ("stderr", sys.__stderr__)):
            if not _usable(getattr(sys, name)):
                if _usable(original):
                    setattr(sys, name, original)
                else:
                    spare = spare or open(os.devnull, "w")  # noqa: SIM115 - ferme plus bas
                    setattr(sys, name, spare)
        yield
    finally:
        sys.stdout, sys.stderr = saved
        if spare is not None:
            spare.close()


def start_process(process: Any) -> None:
    with real_stdio():
        process.start()
