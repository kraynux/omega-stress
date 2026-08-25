# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Detail d'un run : verdict, metriques, acces a l'export."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from omega_stress.interfaces.tui.controllers import history_controller
from omega_stress.interfaces.tui.presenters.run_presenter import (
    chronology_lines,
    diagnostic_message,
    verdict_explanation,
    verdict_label,
)
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.export_dialog import ExportDialogScreen
from omega_stress.interfaces.tui.widgets.stat_card import StatCard

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer


class RunDetailsScreen(OmegaScreen):
    """Detail d'un run precis, identifie par son id (voir screens/history.py,
    action "voir detail")."""

    def __init__(self, *, container: DependencyContainer, run_id: str) -> None:
        super().__init__()
        self._container = container
        self._run_id = run_id

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("DETAIL DU RUN", classes="omega-title")
            with Horizontal(id="stats", classes="omega-stat-row"):
                yield StatCard("Verdict", id="stat-verdict")
                yield StatCard("Debit observe", id="stat-rate")
                yield StatCard("Erreurs", id="stat-errors")
                yield StatCard("Latence p95", id="stat-p95")
            yield Static("", id="verdict-explanation")
            yield Static("", id="summary")
            yield Static("", id="chronology")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter", id="export", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        run = history_controller.run_details(
            self._run_id,
            run_repository=self._container.run_repository,
            target_repository=self._container.target_repository,
        )
        summary = self.query_one("#summary", Static)
        if run is None:
            summary.update(f"Run {self._run_id!r} introuvable.")
            self.query_one("#export", Button).disabled = True
            return

        self.query_one("#stat-verdict", StatCard).update_value(verdict_label(run))
        if run.observed_rate_per_minute is not None:
            self.query_one("#stat-rate", StatCard).update_value(
                f"{run.observed_rate_per_minute:.0f} req/min"
            )
            errors = run.error_count or 0
            total = run.total_requests or 0
            self.query_one("#stat-errors", StatCard).update_value(f"{errors}/{total}")
            p95 = run.p95_latency_ms or 0.0
            self.query_one("#stat-p95", StatCard).update_value(f"{p95:.0f} ms")

        explanation = verdict_explanation(run)
        if explanation:
            self.query_one("#verdict-explanation", Static).update(explanation)

        text = (
            f"{run.id}\nCible : {run.target_address}\nFamille/niveau : {run.family}/{run.level}\n"
            f"Demarre : {run.started_at}"
        )
        reason = diagnostic_message(run)
        if reason:
            text += f"\nDiagnostic : {reason}"
        if run.sample_count:
            text += (
                f"\n{run.sample_count} mesures enregistrees "
                "(detail exhaustif : export JSON/HTML)."
            )
        summary.update(text)

        lines = chronology_lines(run.samples)
        chronology = self.query_one("#chronology", Static)
        if lines:
            chronology.update(
                "Chronologie — temps | taux d'erreur (barre) | erreurs/requetes par palier\n"
                + "\n".join(lines)
            )
        else:
            chronology.update(
                "Aucune mesure enregistree : le test s'est termine avant la premiere "
                "mesure (voir le diagnostic ci-dessus)."
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "export":
            self.app.push_screen(ExportDialogScreen(container=self._container, run_id=self._run_id))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Affiche le detail d'un run identifie par id, point d'entree vers
#   l'export (screens/export_dialog.py).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Delegue tout a controllers/history_controller.py::run_details(), ne
#   recalcule jamais un verdict ou une metrique lui-meme (presenters/
#   run_presenter.py se charge de la mise en forme).
# Ce qu'il ne contient PAS :
# - Aucun tableau exhaustif des IntervalSample bruts (valeurs precises
#   p50/p95/p99, debit par intervalle) : c'est ce que #chronology montre
#   qui compte (2026-08-24, voir Points cles), pas le detail chiffre
#   exact de chaque palier — celui-ci reste dans le contenu d'export
#   (domain/reports/builders.py, chronologie HTML/JSON), pas a l'ecran.
# - Aucune table d'evenements complete ni recommandations construites
#   (ReportDiagnostic) : seule la raison la plus recente (RunDTO.events,
#   via diagnostic_message()) est affichee ici — corrige le 2026-08-24,
#   avant quoi un run FAILED/AUTO_STOPPED n'affichait strictement aucune
#   raison, ni ici ni dans l'export (RunEvent n'etait jamais construit).
# Points cles :
# - Le bouton "Exporter" est desactive si le run est introuvable (jamais
#   d'export sur un id invalide) — coherent avec la verification faite a
#   nouveau par application/commands/export_run_report.py de toute facon.
# - #chronology (2026-08-24) : une ligne par palier via presenters/
#   run_presenter.py::chronology_lines() (regroupe si sample_count est
#   trop grand pour l'ecran). Repond directement a la demande "voir a
#   partir d'ou ca a bloque" sans quitter le TUI, le detail chiffre exact
#   restant reserve a l'export. Message de repli explicite (2026-08-25,
#   remplace un bloc vide sans aucun texte) si `run.samples` est vide
#   (run termine sans aucune mesure, ex. cible injoignable des le
#   premier appel) — bug reel rapporte ("l'interieur du bloc est vide
#   donc on sait pas ce que ca donne ce test") : un bloc silencieusement
#   vide se lisait comme un defaut d'affichage, pas comme une information
#   ("il n'y a rien a montrer, et voici pourquoi").
# - #stats (2026-08-25, StatCard en rangee horizontale, meme widget que
#   widgets/progress_panel.py) : bug reel rapporte ("le rendu est
#   toujours en bloc vertical, il doit etre en horizontale, vu les
#   differentes longueurs") — separe desormais les 4 METRIQUES COURTES
#   (verdict, debit, erreurs, p95 — longueur fixe et comparable) dans une
#   rangee de cartes horizontales, du texte plus LONG et de longueur
#   variable (id, cible, diagnostic — jamais aligne proprement en
#   colonnes) qui reste dans #summary, un bloc vertical classique en
#   dessous. #stat-rate/#stat-errors/#stat-p95 restent vides (StatCard
#   affiche alors son "—" par defaut) tant que le run n'a produit aucune
#   metrique agregee (verdict encore None, cas theorique seulement —
#   cet ecran n'est en pratique jamais pousse sur un run non termine).
# - #verdict-explanation (2026-08-25) : phrase en clair via presenters/
#   run_presenter.py::verdict_explanation() — bug reel rapporte ("quand
#   il y a un verdict, a quoi correspond ce verdict ? verdict degrade par
#   exemple... c'est pas clair") : #stat-verdict n'affiche que le
#   LIBELLE court ("Degrade"), jamais suffisant seul pour un lecteur qui
#   ne connait pas deja la signification produit de chaque verdict.
# Comment il sera utilise :
# - interfaces/tui/screens/history.py (action "voir detail").
# - Les 3 ecrans de lancement (2026-08-24) poussent directement cet ecran
#   apres un run termine avec succes (Ok(RunDTO)) au lieu de se contenter
#   d'une ligne dans #result — voir leur propre INFO DEV
#   (screens/request_panel.py notamment).
#---------------------------------------------------------------------->
