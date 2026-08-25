# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Petite carte affichant un libelle et une valeur, reutilisee dans les tableaux de bord."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class StatCard(Vertical):
    """Une statistique isolee (ex. "Debit observe" / "248 req/min")."""

    DEFAULT_CSS = """
    StatCard {
        width: 24;
        height: 2;
        padding: 0 2;
    }
    """

    def __init__(
        self,
        label: str,
        value: str = "—",
        *,
        name: str | None = None,
        id: str | None = None,  # noqa: A002 - nom impose par l'API Textual
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._label = label
        self._value = value

    def compose(self) -> ComposeResult:
        yield Static(self._label, classes="omega-subtitle")
        yield Static(self._value, id="value")

    def update_value(self, value: str) -> None:
        self._value = value
        self.query_one("#value", Static).update(value)

# <-- INFO DEV ---------------------------------------------------------
# Role : brique d'affichage generique label/valeur, sans connaissance du
# domaine — reutilisee par progress_panel.py et d'autres ecrans.
# Pourquoi dans interfaces/tui/widgets/ (charte) : widget de presentation
# pur, aucune logique metier, aucun appel a application/.
# Ce qu'il ne contient PAS : aucune mise a jour automatique/timer — c'est
# l'appelant (ex. ProgressPanel) qui pousse les valeurs via update_value().
# Points cles :
# - width/height CHIFFRES, pas "auto" (2026-08-25, corrige un bug reel
#   rapporte : "la jauge... le compteur aussi a disparu") : verifie en
#   introspection ET en capture d'ecran reelle, "width: auto; height:
#   auto;" (valeur d'origine) mesurait ce widget (Vertical, lui-meme
#   imbrique dans un Horizontal) a une taille de 0x0 malgre un contenu
#   textuel non vide (les deux Static enfants portaient bien le bon texte,
#   leur content_size restait pourtant a Size(0, 0)) — StatCard restait
#   donc invisible en pratique, quelles que soient les valeurs poussees
#   par update_value(). Cause exacte non identifiee avec certitude (piste
#   probable : mesure "auto" non fiable sur plusieurs niveaux de
#   conteneurs "auto" imbriques dans ce conteneur Textual precis), mais
#   des dimensions fixes contournent le probleme de facon verifiee. 24
#   (largeur) accommode le plus long libelle/valeur reellement affiche
#   ("Latence p95", "Arret automatique") avec la marge du padding.
# Comment il sera utilise : interfaces/tui/widgets/progress_panel.py,
# screens/run_details.py.
#---------------------------------------------------------------------->
