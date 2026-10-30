# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Selection d'une cible : liste epinglee/recente, ou saisie manuelle."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Label, OptionList
from textual.widgets.option_list import Option

from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.shared.i18n import _


class TargetPicker(Vertical):
    """Combine une liste de cibles connues et un champ de saisie libre."""

    DEFAULT_CSS = """
    TargetPicker {
        height: 12;
    }
    TargetPicker > #known-targets {
        height: 8;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(_("Cible"), classes="omega-subtitle")
        yield OptionList(id="known-targets")
        yield Input(
            placeholder=_("ou saisir une adresse (ex. https://exemple.org)"),
            id="manual-target",
        )

    def load_targets(self, targets: tuple[TargetDTO, ...]) -> None:
        option_list = self.query_one("#known-targets", OptionList)
        option_list.clear_options()
        for target in targets:
            marker = "* " if target.pinned else "  "
            option_list.add_option(Option(f"{marker}{target.base_url}", id=target.id))

    @property
    def manual_value(self) -> str:
        return self.query_one("#manual-target", Input).value

    @manual_value.setter
    def manual_value(self, value: str) -> None:
        self.query_one("#manual-target", Input).value = value

# <-- INFO DEV ---------------------------------------------------------
# Role : composant de choix de cible reutilise par les 3 ecrans de
# lancement (request/connection/ramp).
# Pourquoi dans interfaces/tui/widgets/ (charte) : pas de validation
# metier ici — l'adresse saisie est validee par
# application/commands/run_precheck.py (via domain/target/policies.py),
# jamais dans l'interface.
# Ce qu'il ne contient PAS : le marqueur "*" est en ASCII pur (pas
# d'emoji) pour rester lisible aussi en profil `mono`/`reduced`.
# Points cles : le setter de manual_value (2026-08-24) permet a un ecran
# de PRE-REMPLIR le champ (ex. cible par defaut d'un profil fige
# selectionne) sans connaitre l'id interne "#manual-target" — seule cette
# classe sait ou vit reellement le champ de saisie libre.
# - DEFAULT_CSS height:12/#known-targets height:8 (2026-09-27, bug reel
#   rapporte et confirme par capture d'ecran reelle ET par
#   export_screenshot() en test : "Cible" (le Label) restait seul
#   visible, suivi DIRECTEMENT du titre de la section suivante — aucune
#   trace de l'OptionList ni de l'Input, quel que soit leur nombre de
#   cibles connues) : meme famille de cause EXACTE que widgets/
#   run_progress.py::RunProgress (voir son propre INFO DEV, correctif du
#   2026-08-25) — TargetPicker(Vertical) heritait de height:1fr
#   (textual.containers.Vertical.DEFAULT_CSS) SANS jamais etre corrige ;
#   Vertical porte aussi overflow:hidden par defaut, donc des que le
#   "1fr" alloue par le parent (".omega-panel", lui-meme scrollable mais
#   ne calcule ce "1fr" que sur le champ de vue, pas sur toute l'etendue
#   scrollable) devenait plus petit que le contenu naturel (Label +
#   OptionList + Input, ~7 lignes minimum), l'exces etait purement et
#   simplement DECOUPE (hidden), sans aucune barre de defilement propre
#   a ce widget — le Label seul rentrait dans l'espace restant, le
#   reste disparaissait. Introspection directe (Widget.size/.region)
#   AVANT ce correctif rapportait pourtant des hauteurs non nulles
#   (OptionList/Input a 1) : la mesure de layout differait du rendu
#   reellement PEINT par le compositeur — seul export_screenshot() (ou
#   un vrai terminal) revele l'ecart, jamais Widget.size seul (meme
#   avertissement deja documente dans run_progress.py). Hauteurs
#   CHIFFREES plutot que "auto"/"1fr" imbriques : 12 = Label (1) +
#   OptionList (8) + Input (3, deja fixe nativement dans le DEFAULT_CSS
#   Textual d'Input, jamais recouvert ici). OptionList a 8 (bordure
#   haute/basse incluses) plutot qu'une hauteur couvrant le maximum
#   theorique de cibles (cibles epinglees illimitees + jusqu'a 10
#   recentes, voir README "Cibles epinglees") : OptionList gere son
#   propre defilement INTERNE au-dela de sa hauteur fixee, contrairement
#   au Vertical parent — aucune perte de cibles, juste un defilement a
#   l'interieur du widget si plus de ~6 options.
# Comment il sera utilise : screens/request_panel.py, connection_panel.py,
# ramp_panel.py, profile_wizard.py.
#---------------------------------------------------------------------->
