# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Alias de type transverses reutilises dans les signatures de commands/queries."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

IdFactory = Callable[[], str]
"""Signature d'un generateur d'identifiant injecte dans un command de
creation (voir shared/ids.py::new_id, l'implementation de production)."""

Clock = Callable[[], datetime]
"""Signature d'une horloge injectee, appelee PLUSIEURS fois au cours d'une
meme action (voir shared/clock.py::utc_now, l'implementation de production)
— reservee au seul chemin d'execution d'un run (application/pipeline/
executor.py et abort.py, application/commands/run_precheck.py et
_launch_support.py::launch_plan()) : cette action a une duree reelle
(l'appel a ports/load_runner.py::LoadRunner.run() peut durer plusieurs
minutes), contrairement aux autres commands ou `now` reste une valeur
`datetime` figee (voir shared/clock.py, INFO DEV)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Regroupe les alias de type reutilises dans plusieurs signatures de
#   command/query, pour eviter de repeter des types composes (Callable[...])
#   a chaque fichier.
# Pourquoi dans shared/ (charte) :
# - Utilitaire transverse non metier, purement outillage de typage.
# Ce qu'il ne contient PAS :
# - Aucun type portant une signification metier (ces types-la vivent dans
#   domain/ ou core/enums.py) : uniquement des formes de fonctions
#   d'infrastructure legere (generation d'id, etc.).
# Points cles :
# - Volontairement tres court : n'y ajouter un alias que lorsqu'il est
#   reellement reutilise par au moins deux command/query differents.
# - Clock (2026-08-27, correction de bug reel) : AVANT ce correctif, tout
#   `now` du projet (y compris application/pipeline/executor.py) etait une
#   valeur `datetime` figee, capturee UNE FOIS par
#   interfaces/tui/controllers/*.py ou interfaces/cli/commands/*.py avant
#   d'appeler le command — correct pour une action instantanee
#   (create_profile, pin_target...), mais faux pour l'execution d'un run :
#   la meme valeur figee, capturee AVANT le `async for sample in
#   load_runner.run(...)` de l'executor (potentiellement plusieurs
#   minutes), etait ensuite reutilisee TELLE QUELLE comme finished_at —
#   donc started_at == finished_at == duree 0.0 min dans TOUS les
#   rapports exportes, quelle que soit la duree reelle du run. Clock
#   corrige cela en appelant `now()` fraichement a chaque cloture
#   (executor.py/abort.py), plutot qu'en reutilisant une seule valeur
#   capturee avant le debut de l'execution.
# Comment il sera utilise (apercu) :
# - application/commands/create_profile.py et les futures commandes de
#   creation typent leur parametre `id_factory: IdFactory`.
# - application/pipeline/executor.py, abort.py, application/commands/
#   run_precheck.py, _launch_support.py (et les quatre commands run_*_load/
#   replay_run.py qui la traversent) typent leur parametre `now: Clock`.
#---------------------------------------------------------------------->
