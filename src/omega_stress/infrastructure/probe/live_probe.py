# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation concrete du port SystemSampler : sondage systeme
CONTINU, appele une fois par intervalle pendant un run (Phase 1
observabilite). Seul point du projet ou `psutil` est importe (contrat
import-linter dedie, voir pyproject.toml)."""
from __future__ import annotations

import psutil

from omega_stress.domain.runs.models import SystemSnapshot
from omega_stress.infrastructure.probe.limits_reader import read_open_file_limit

_BYTES_PER_MB = 1024 * 1024


class LiveSystemSampler:
    """Implemente ports/system_sampler.py::SystemSampler.

    Garde un psutil.Process() en instance (pas recree a chaque appel) :
    psutil.Process.cpu_percent()/psutil.cpu_percent() mesurent un DELTA
    depuis le dernier appel — un objet recree a chaque sample() mesurerait
    toujours 0.0 (aucun historique entre deux appels)."""

    def __init__(self) -> None:
        self._process = psutil.Process()
        # Premier appel purement pour amorcer le compteur interne (delta
        # non exploitable avant un second appel, voir doc psutil) —
        # jamais interprete, seule la valeur des sample() suivants compte.
        self._process.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None)
        # Nombre de coeurs logiques, lu UNE FOIS (ne change pas en cours
        # de run) : psutil.Process.cpu_percent() n'est PAS normalise par
        # le nombre de coeurs (documentation psutil) — un processus qui
        # sature un seul coeur affiche ~100% quel que soit le nombre de
        # coeurs disponibles par ailleurs (bug reel corrige le 2026-09-01 :
        # un run "Maximum" s'arretait au bout de 3s, diagnostic ">90%",
        # alors que l'utilisation globale machine restait ~20% — le moteur
        # asyncio, lie au GIL, ne peut de toute facon utiliser qu'un seul
        # coeur pour ce workload). Diviser par le nombre de coeurs remet
        # cpu_percent_generator sur la meme echelle 0-100 que
        # cpu_percent_global, coherent avec le document (tableau
        # "Preconditions du calibrage", les deux valeurs lues ensemble).
        self._logical_cpu_count: int = psutil.cpu_count() or 1
        # Limite douce de FDs lue UNE FOIS (Phase 2 garde-fous) : un
        # ulimit ne change pas en cours de run, inutile de re-appeler
        # resource.getrlimit() a chaque sample() — reportee telle quelle
        # sur chaque SystemSnapshot pour que domain/load/validators.py
        # calcule un ratio en pur domaine (voir infrastructure/probe/
        # limits_reader.py, deja utilise par local_probe.py).
        try:
            self._open_files_soft_limit: int | None = read_open_file_limit()[0]
        except OSError:
            self._open_files_soft_limit = None

    def sample(self) -> SystemSnapshot:
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return SystemSnapshot(
                cpu_percent_generator=(
                    self._process.cpu_percent(interval=None) / self._logical_cpu_count
                ),
                cpu_percent_global=psutil.cpu_percent(interval=None),
                memory_available_percent=(
                    (memory.available / memory.total) * 100 if memory.total else None
                ),
                memory_rss_mb=self._process.memory_info().rss / _BYTES_PER_MB,
                swap_used_mb=swap.used / _BYTES_PER_MB,
                open_files=self._safe_open_files(),
                open_files_soft_limit=self._open_files_soft_limit,
                logical_cpu_count=self._logical_cpu_count,
            )
        except psutil.Error:
            # Une mesure systeme manquee ne doit jamais faire echouer un
            # run (voir domain/runs/models.py::SystemSnapshot) : un
            # snapshot entierement a None reste un resultat valide.
            return SystemSnapshot()

    def _safe_open_files(self) -> int | None:
        """num_fds() n'existe que sur Unix (AttributeError sous Windows,
        hors perimetre de ce projet mais garde defensivement) — separe du
        try/except principal pour qu'un echec ici ne prive pas les autres
        champs deja lus avec succes."""
        try:
            return int(self._process.num_fds())
        except (psutil.Error, AttributeError):
            return None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Sonde CPU/RAM/swap/FDs du generateur et du systeme, une fois par
#   intervalle pendant un run — jamais au pre-flight (voir local_probe.py
#   pour ce cas distinct).
# Pourquoi dans infrastructure/probe/ (charte) :
# - Meme sous-domaine technique que local_probe.py (sondage systeme),
#   mais portee temporelle differente (continu vs une fois) — deux
#   fichiers separes plutot qu'un seul avec un mode, pour ne jamais
#   confondre les deux contrats de port (system_probe vs system_sampler).
# Ce qu'il ne contient PAS :
# - Aucun seuil numerique (voir domain/load/policies.py::
#   GENERATOR_CPU_WARNING_THRESHOLD, consomme par domain/reports/
#   builders.py, jamais compare ici).
# - Aucune decision d'arret : ce fichier mesure, ne juge jamais.
# Points cles :
# - open_files_soft_limit (Phase 2 garde-fous) : lu une seule fois dans
#   __init__(), jamais re-lu dans sample() — evite un appel syscall
#   inutile a chaque intervalle pour une valeur qui ne change pas en
#   cours de run.
# - sample() n'est JAMAIS bloquant (interval=None partout) : un
#   generateur qui emet des dizaines de requetes par seconde ne peut pas
#   se permettre un sample() qui attend 1 seconde pour un pourcentage
#   CPU precis (comportement par defaut de psutil.cpu_percent() sans cet
#   argument) — la mesure est donc le delta depuis le dernier appel, pas
#   une moyenne sur une fenetre fixe.
# - psutil.Error jamais laissee remonter : une mesure systeme est un
#   detail secondaire du run, jamais une raison de l'interrompre.
# - cpu_percent_generator / _logical_cpu_count (2026-09-01, correction de
#   bug reel en 2 temps) : psutil.Process.cpu_percent() renvoie un
#   pourcentage NON normalise par le nombre de coeurs (peut depasser
#   100% sur un processus multi-thread, ou simplement plafonner pres de
#   100% des qu'UN SEUL coeur est sature) — sur une machine multi-coeurs,
#   le moteur asyncio (lie au GIL, ne peut utiliser qu'un seul coeur pour
#   ce workload) affichait ~100% des qu'il devenait actif, quel que soit
#   le nombre de coeurs libres par ailleurs. Premier correctif : diviser
#   par le nombre de coeurs logiques (lu une fois ici, ne change pas en
#   cours de run) remet cpu_percent_generator sur la meme echelle 0-100
#   que cpu_percent_global, coherent avec le document produit (tableau
#   "Preconditions du calibrage" lit les deux valeurs ensemble comme si
#   elles etaient deja comparables). Insuffisant seul : un moteur
#   mono-coeur pleinement sature n'atteint alors plus jamais 90% des 4
#   coeurs (~25% normalise au mieux), rendant le seuil d'arret quasiment
#   inerte — second correctif (domain/load/policies.py::
#   GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE, domain/load/validators.py::
#   _single_core_abort_threshold()) : logical_cpu_count est aussi
#   transmis sur chaque SystemSnapshot pour que le seuil d'arret
#   lui-meme reste RELATIF a ce qu'un seul coeur peut fournir sur la
#   machine courante, plutot qu'un pourcentage absolu fixe — condition
#   necessaire pour un produit distribue sur des machines heterogenes
#   (1 a N coeurs).
# Comment il sera utilise (apercu) :
# - infrastructure/runner/httpx_load_generator.py instancie
#   LiveSystemSampler() par defaut si aucun SystemSampler n'est injecte.
#---------------------------------------------------------------------->
