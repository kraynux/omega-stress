# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : libelles humains pour l'affichage d'un run (detail ou ligne)."""
from __future__ import annotations

import math

from omega_stress.application.dto.run_dto import IntervalSampleDTO, RunDTO
from omega_stress.core.enums import RunVerdict
from omega_stress.domain.reports.builders import VERDICT_HEADLINES

_VERDICT_LABELS: dict[str, str] = {
    "success": "Reussi",
    "degraded": "Degrade",
    "auto_stopped": "Arret automatique",
    "failed": "Echec",
}

_CHRONOLOGY_MAX_ROWS = 15
_CHRONOLOGY_BAR_WIDTH = 20


def verdict_label(run: RunDTO) -> str:
    """Libelle humain du verdict, ou "En cours" tant que le run n'est pas
    termine (RunDTO.verdict est None dans ce cas)."""
    if run.verdict is None:
        return "En cours"
    return _VERDICT_LABELS.get(run.verdict, run.verdict)


def verdict_explanation(run: RunDTO) -> str:
    """Phrase en clair expliquant CE QUE SIGNIFIE le verdict (pas
    seulement son libelle) — chaine vide tant que le run est en cours
    (aucun verdict decide)."""
    if run.verdict is None:
        return ""
    return VERDICT_HEADLINES.get(RunVerdict(run.verdict), "")


def diagnostic_message(run: RunDTO) -> str:
    """Raison du dernier evenement du run (echec technique ou arret
    automatique), ou chaine vide s'il n'y en a aucun — cas normal d'un
    run en cours, reussi, ou degrade sans evenement notable."""
    if not run.events:
        return ""
    return run.events[-1].message


def metrics_summary(run: RunDTO) -> str:
    """Resume compact des metriques d'un run termine ; chaine vide tant
    que le run est en cours (aucune metrique agregee disponible)."""
    if run.observed_rate_per_minute is None:
        return ""
    errors = run.error_count or 0
    total = run.total_requests or 0
    p95 = run.p95_latency_ms or 0.0
    return (
        f"{run.observed_rate_per_minute:.0f} req/min | "
        f"{errors}/{total} erreurs | p95 {p95:.0f} ms"
    )


def chronology_lines(samples: tuple[IntervalSampleDTO, ...]) -> tuple[str, ...]:
    """Une ligne par intervalle (ou par palier regroupe si `samples`
    depasse _CHRONOLOGY_MAX_ROWS), barre ASCII proportionnelle au taux
    d'erreur du palier. Tuple vide si `samples` est vide (run en cours,
    ou run termine sans aucune mesure — precheck rejete avant la premiere
    mesure par exemple)."""
    if not samples:
        return ()
    bucket_size = max(1, math.ceil(len(samples) / _CHRONOLOGY_MAX_ROWS))
    lines: list[str] = []
    for start in range(0, len(samples), bucket_size):
        chunk = samples[start : start + bucket_size]
        errors = sum(s.error_count for s in chunk)
        requests = sum(s.request_count for s in chunk)
        ratio = errors / requests if requests else 0.0
        filled = round(ratio * _CHRONOLOGY_BAR_WIDTH)
        bar = "█" * filled + "░" * (_CHRONOLOGY_BAR_WIDTH - filled)
        lines.append(f"{chunk[0].at_second:>5.0f}s  {bar}  {errors} err / {requests} req")
    return tuple(lines)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit les champs bruts d'un RunDTO (application/dto/run_dto.py) en
#   texte pret pour l'affichage.
# Pourquoi dans interfaces/tui/presenters/ (charte) :
# - _VERDICT_LABELS est un vocabulaire de PRESENTATION (francais, pour
#   l'ecran), distinct du vocabulaire normatif RunVerdict (core/enums.py) :
#   ne doit jamais remonter dans core/ ni domain/.
# Ce qu'il ne contient PAS :
# - Aucune decision de verdict (celle-ci vient de
#   domain/runs/service.py::finish(), deja figee dans RunDTO.verdict) :
#   ce module ne fait que formater une valeur deja decidee.
# Points cles :
# - verdict_explanation() (2026-08-25) : reutilise domain/reports/
#   builders.py::VERDICT_HEADLINES (renommee publique le meme jour,
#   utilisee jusque-la seulement par l'export) plutot que d'inventer un
#   second texte ici — bug reel rapporte ("verdict degrade par exemple...
#   a quoi correspond ce verdict ?", screens/run_details.py n'affichait
#   QUE le libelle court avant ce correctif, jamais d'explication). Une
#   seule formulation par verdict, partagee entre export et ecran de
#   detail.
# - metrics_summary() teste observed_rate_per_minute (jamais verdict) pour
#   decider si des metriques existent : coherent avec l'invariant
#   documente dans run_dto.py (tous les champs de resultat sont None
#   ensemble).
# - diagnostic_message() (2026-08-24) ne garde que le DERNIER evenement :
#   en V1 un run ne produit jamais plus d'un evenement (un seul abort ou
#   un seul RunnerFailureError met fin au run), donc "dernier" et "seul"
#   coincident toujours en pratique — a revoir seulement si un jour un run
#   peut accumuler plusieurs evenements avant de se terminer.
# - chronology_lines() (2026-08-24) : regroupe en paliers (bucket_size,
#   round-robin par tranches contigues) des que len(samples) depasse
#   _CHRONOLOGY_MAX_ROWS (15, volontairement conservateur : un run au
#   niveau maximum peut produire jusqu'a plusieurs centaines de
#   IntervalSample, et screens/run_details.py n'est pas un ecran defilant
#   dedie — 15 lignes plus le resume tiennent sans defilement sur un
#   terminal a la taille minimale supportee, MINIMUM_USABLE_ROWS=24,
#   domain/terminal/policies.py, ce que 40 ne garantissait pas, verifie en
#   pilote). La
#   barre (_CHRONOLOGY_BAR_WIDTH=20 caracteres pleins/vides) est
#   proportionnelle au taux d'erreur AGREGE du palier (somme erreurs /
#   somme requetes du groupe), pas a la moyenne des taux individuels —
#   evite qu'un palier avec peu de requetes mais 100% d'erreurs pese
#   autant qu'un palier avec beaucoup de requetes et le meme taux.
# - "{errors} err / {requests} req" (2026-08-25, remplace "{errors}/
#   {requests}" nu) : bug reel rapporte ("0/9 ça veut dire quoi ?") — le
#   format brut se lisait comme un score sportif ou une fraction sans
#   unite, aucun moyen de deviner ce que chaque nombre representait sans
#   deja connaitre le code. Les libelles complets ("erreurs"/"requetes")
#   ne sont pas repetes ligne par ligne (jusqu'a 15 lignes) : un en-tete
#   explique le format une seule fois (screens/run_details.py), ces
#   abreviations restent lisibles une fois l'en-tete lu.
# Comment il sera utilise :
# - screens/request_panel.py, connection_panel.py, ramp_panel.py (raison
#   affichee en complement de metrics_summary() quand celle-ci est vide),
#   screens/run_details.py (chronology_lines() et verdict_explanation()
#   y compris), widgets/history_table.py (colonne verdict).
#---------------------------------------------------------------------->
