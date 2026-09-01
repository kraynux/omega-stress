# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Construction du contenu logique d'un rapport a partir d'un run termine."""
from __future__ import annotations

from omega_stress.core.enums import RunVerdict
from omega_stress.domain.load.policies import (
    GENERATOR_CPU_WARNING_THRESHOLD,
    LOCAL_BOTTLENECK_RATIO_THRESHOLD,
)
from omega_stress.domain.reports.models import ReportContent, ReportDiagnostic, ReportSummary
from omega_stress.domain.runs.models import LoadResult, LoadRun

VERDICT_HEADLINES: dict[RunVerdict, str] = {
    RunVerdict.SUCCESS: "Le test s'est deroule normalement, sans depassement de seuil.",
    RunVerdict.DEGRADED: (
        "Le test s'est termine avec une degradation observee, sans depassement de seuil critique."
    ),
    RunVerdict.AUTO_STOPPED: (
        "Le test a ete arrete automatiquement suite a un depassement de seuil."
    ),
    RunVerdict.FAILED: "Le test a echoue avant d'avoir pu produire un resultat exploitable.",
}

MANUAL_STOP_HEADLINE = "Le test a ete arrete manuellement par l'utilisateur."
"""Bug reel rapporte (2026-09-01, capture d'ecran fournie) : un arret
manuel (bouton "Arreter") partage le verdict AUTO_STOPPED avec un arret
automatique par seuil (voir application/pipeline/executor.py, INFO DEV,
"ces deux motifs partagent le meme sens produit") — VERDICT_HEADLINES
indexe seulement par verdict affichait donc "arrete... suite a un
depassement de seuil" MEME pour un arret manuel, en contradiction directe
avec le diagnostic (dernier RunEvent, kind="manual_stop", message "Arrete
manuellement par l'utilisateur.") affiche juste en dessous — deux
messages contradictoires sur le meme ecran. verdict_headline() ci-dessous
distingue desormais les deux cas via RunEvent.kind, jamais le verdict
seul."""


def verdict_headline(verdict: RunVerdict, *, last_event_kind: str | None = None) -> str:
    """Libelle explicatif d'un verdict, en tenant compte du DERNIER
    evenement quand le verdict seul est ambigu (AUTO_STOPPED : seuil
    depasse OU arret manuel, memes verdict, causes distinctes — voir
    MANUAL_STOP_HEADLINE ci-dessus). Point d'entree UNIQUE, remplace tout
    acces direct a VERDICT_HEADLINES[...] : jamais deux endroits qui
    pourraient diverger sur ce cas particulier."""
    if verdict is RunVerdict.AUTO_STOPPED and last_event_kind == "manual_stop":
        return MANUAL_STOP_HEADLINE
    return VERDICT_HEADLINES[verdict]


def build_report_content(run: LoadRun, *, target_address: str) -> ReportContent:
    """Assemble le contenu logique d'un rapport pour un run termine.

    Leve ValueError si le run n'est pas termine : appeler ceci sur un run
    en cours est une erreur de programmation de l'appelant
    (application/commands/export_run_report.py doit verifier
    run.finished_at avant d'appeler cette fonction), pas un echec metier
    attendu du parcours utilisateur.
    """
    if run.finished_at is None or run.result is None:
        raise ValueError(
            f"Le run {run.id} n'est pas termine, aucun rapport ne peut etre construit."
        )

    duration_minutes = (run.finished_at - run.started_at).total_seconds() / 60.0

    summary = ReportSummary(
        run_id=run.id,
        target_address=target_address,
        family=run.family,
        level=run.level,
        started_at=run.started_at,
        finished_at=run.finished_at,
        duration_minutes=duration_minutes,
        duration_preset_id=run.duration_preset_id,
        safety_mode=run.safety_mode,
    )
    diagnostic = _build_diagnostic(run.result)
    return ReportContent(summary=summary, result=run.result, diagnostic=diagnostic)


def _build_diagnostic(result: LoadResult) -> ReportDiagnostic:
    last_event_kind = result.events[-1].kind if result.events else None
    headline = verdict_headline(result.verdict, last_event_kind=last_event_kind)
    recommendations: list[str] = [event.message for event in result.events]

    if result.error_count > 0:
        recommendations.append(
            f"{result.error_count} erreur(s) sur {result.total_requests} requetes : "
            f"verifier les journaux de la cible sur la periode du test."
        )

    if (
        result.requested_rate_per_minute is not None
        and result.observed_rate_per_minute is not None
        and result.observed_rate_per_minute
        < result.requested_rate_per_minute * LOCAL_BOTTLENECK_RATIO_THRESHOLD
    ):
        recommendations.append(
            "Debit observe significativement inferieur au debit demande : "
            "le generateur local peut etre devenu le goulot d'etranglement "
            "(voir plan produit, Configuration minimale du generateur)."
        )

    if (
        result.peak_cpu_percent_generator is not None
        and result.peak_cpu_percent_generator >= GENERATOR_CPU_WARNING_THRESHOLD
    ):
        recommendations.append(
            f"CPU du generateur monte a {result.peak_cpu_percent_generator:.0f} % au pic "
            f"pendant le test : les resultats peuvent en partie refleter une limite du "
            f"generateur local plutot que celle de la cible."
        )

    return ReportDiagnostic(
        verdict=result.verdict, headline=headline, recommendations=tuple(recommendations)
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - build_report_content() : point d'entree unique pour transformer un
#   LoadRun termine en ReportContent pret a etre serialise par
#   infrastructure/exporters/.
# - _build_diagnostic() : construit la box diagnostic (headline +
#   recommandations) a partir du verdict et des metriques.
# Pourquoi dans domain/reports/ (charte) :
# - Logique metier pure de construction, sans I/O, sans dependance a un
#   format de sortie.
# Ce qu'il ne contient PAS :
# - Aucune ecriture disque (voir infrastructure/exporters/).
# - Aucune connaissance du theme d'export (c'est
#   infrastructure/exporters/html_theme_resolver.py, uniquement pertinent
#   pour le format HTML).
# Points cles :
# - build_report_content() leve ValueError (pas un Result) pour un run non
#   termine : c'est un garde-fou de precondition d'appel, pas un echec
#   metier attendu (voir docstring de la fonction pour la justification).
# - Le seuil de detection de goulot d'etranglement local (10%) vit dans
#   domain/load/policies.py::LOCAL_BOTTLENECK_RATIO_THRESHOLD, partage
#   avec application/pipeline/degraded_mode.py qui l'evalue en direct
#   pendant le run — jamais duplique ici.
# - Les recommandations sont une liste ouverte construite au cas par cas :
#   ajouter une nouvelle regle de diagnostic ici, jamais dans
#   l'infrastructure d'export ni dans la presentation.
# - result.events (2026-08-24) est reverse en tete de liste tel quel : ce
#   sont deja des messages phrases pour un lecteur (raison d'un
#   RunnerFailureError ou d'un ThresholdExceededError, voir
#   application/pipeline/executor.py et abort.py), pas des donnees brutes
#   a interpreter ici — coherent avec la note deja presente sur
#   LoadResult.events dans domain/runs/models.py ("deja portee par
#   LoadResult.events (RunEvent) si pertinent, pas dupliquee ici").
# - VERDICT_HEADLINES (2026-08-25, renommee depuis _HEADLINES — devenue
#   publique) : desormais aussi consommee par interfaces/tui/presenters/
#   run_presenter.py::verdict_explanation(), pour que
#   screens/run_details.py explique en clair CE QUE SIGNIFIE un verdict
#   (bug reel rapporte : "verdict degrade par exemple... a quoi correspond
#   ce verdict ?") — une seule formulation par verdict, partagee entre
#   l'export et l'ecran de detail, jamais deux textes qui pourraient
#   diverger.
# - verdict_headline()/MANUAL_STOP_HEADLINE (2026-09-01, bug reel rapporte
#   avec capture d'ecran) : VERDICT_HEADLINES seul ne distingue pas les
#   deux causes d'AUTO_STOPPED (seuil depasse / arret manuel), produisant
#   un ecran contradictoire ("...suite a un depassement de seuil" au-
#   dessus de "Arrete manuellement par l'utilisateur." juste en dessous).
#   _build_diagnostic() et run_presenter.py::verdict_explanation()
#   passent tous deux desormais par cette fonction plutot que d'indexer
#   VERDICT_HEADLINES directement — VERDICT_HEADLINES reste public (garde
#   son sens pour SUCCESS/DEGRADED/FAILED, jamais ambigus) mais ne doit
#   plus etre indexe directement pour AUTO_STOPPED en dehors de cette
#   fonction.
# Comment il sera utilise (apercu) :
# - application/commands/export_run_report.py appelle
#   build_report_content() puis passe le resultat a
#   infrastructure/exporters/ via le port report_exporter.
# - interfaces/tui/presenters/run_presenter.py::verdict_explanation() lit
#   VERDICT_HEADLINES directement (domain/ reste en amont d'interfaces/,
#   sens de dependance autorise).
#---------------------------------------------------------------------->
