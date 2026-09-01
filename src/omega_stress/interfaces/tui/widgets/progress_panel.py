# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Affiche la progression en direct d'un run (debit, erreurs, latence)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal

from omega_stress.domain.runs.models import IntervalSample
from omega_stress.interfaces.tui.widgets.stat_card import StatCard


class ProgressPanel(Horizontal):
    """Trois StatCard mis a jour a chaque IntervalSample publie par le run."""

    DEFAULT_CSS = """
    ProgressPanel {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield StatCard("Debit observe", id="rate")
        yield StatCard("Erreurs", id="errors")
        yield StatCard("Latence p95", id="p95")
        yield StatCard("CPU / RAM", id="system")

    def update_sample(self, sample: IntervalSample) -> None:
        self.query_one("#rate", StatCard).update_value(
            f"{sample.observed_rate_per_minute:.0f} req/min"
        )
        self.query_one("#errors", StatCard).update_value(
            f"{sample.error_count}/{sample.request_count}"
        )
        self.query_one("#p95", StatCard).update_value(f"{sample.p95_latency_ms:.0f} ms")
        self.query_one("#system", StatCard).update_value(_format_system(sample))


def _format_system(sample: IntervalSample) -> str:
    """"?" pour un champ non mesurable (voir domain/runs/models.py::
    SystemSnapshot) plutot qu'un vide ambigu ou une exception."""
    if sample.system is None:
        return "? / ?"
    cpu = sample.system.cpu_percent_generator
    memory = sample.system.memory_rss_mb
    cpu_text = f"{cpu:.0f}%" if cpu is not None else "?"
    memory_text = f"{memory:.0f} Mo" if memory is not None else "?"
    return f"{cpu_text} / {memory_text}"

# <-- INFO DEV ---------------------------------------------------------
# Role : traduit un IntervalSample (domain/runs/models.py) en affichage
# textuel, sans logique de calcul propre (les moyennes/ratios sont deja
# calcules par le pipeline avant publication).
# Pourquoi dans interfaces/tui/widgets/ (charte) : widget de presentation,
# lit un objet domain en lecture seule, n'importe rien d'application/.
# Ce qu'il ne contient PAS : aucun abonnement/polling — c'est le
# controller (load_controller.py) qui appelle update_sample() a chaque
# notification recue via le port RunProgressNotifier.
# Points cles :
# - 4e StatCard "CPU / RAM" (Phase 1 observabilite) : affiche "?" par
#   champ non mesurable (sample.system peut etre None, ou un champ
#   individuel None si psutil a echoue sur cette lecture — voir
#   infrastructure/probe/live_probe.py) plutot qu'un vide ambigu.
# - DEFAULT_CSS height:auto (2026-08-25) : Horizontal (classe parente)
#   vaut height:1fr par defaut (occupe tout l'espace vertical restant du
#   panneau, souvent plusieurs dizaines de lignes) — combine a
#   overflow:hidden (autre defaut de Horizontal), les StatCard enfants
#   (eux-memes height:auto) se retrouvaient mesures a une hauteur de 0 et
#   une largeur de 4 caracteres, invisibles en pratique quel que soit le
#   contenu qu'on leur passe via update_value() (verifie : le texte etait
#   bien mis a jour, seule la geometrie du widget etait degenere). Bug
#   reel rapporte ("la jauge... le compteur aussi a disparu") : ce widget
#   affiche precisement ce "compteur" (debit/erreurs/latence en direct).
#   height:auto force ce widget a se dimensionner sur ses propres enfants
#   au lieu de s'etendre — meme cause racine et meme correctif que
#   screens/confirm.py::.omega-confirm-buttons et screens/home.py::
#   .omega-home-menu (voir styles/base.tcss), un widget "1fr" imbrique
#   dans un parent qui n'attend pas cette extension.
# Comment il sera utilise : screens/request_panel.py, connection_panel.py,
# ramp_panel.py (ecrans de lancement de run).
#---------------------------------------------------------------------->
