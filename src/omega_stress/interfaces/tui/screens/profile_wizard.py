# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran assistant : creation d'un nouveau profil de test."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, OptionList, Select, Static

from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err
from omega_stress.interfaces.tui.controllers import load_controller, profile_controller
from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.widgets.target_picker import TargetPicker

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer

_FAMILY_OPTIONS = [(family.value, family) for family in TestFamily]
_LEVEL_OPTIONS = [(level.value, level) for level in IntensityLevel]


class ProfileWizardScreen(OmegaScreen):
    """Formulaire de creation d'un profil non fige (le figer est une
    action separee, voir screens/profiles.py)."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_target: TargetDTO | None = None
        self._targets_by_index: dict[int, TargetDTO] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("NOUVEAU PROFIL", classes="omega-title")
            yield Input(placeholder="Nom du profil", id="name")
            yield Input(placeholder="Description (optionnelle)", id="description")
            yield TargetPicker(id="target-picker")
            yield Select(_FAMILY_OPTIONS, prompt="Famille de test", id="family", allow_blank=False)
            yield Select(_LEVEL_OPTIONS, prompt="Intensite", id="level", allow_blank=False)
            yield Input(placeholder="Duree (minutes)", id="duration")
            yield Input(placeholder="Taux d'erreur maximal (0.0-1.0)", id="max-error-rate")
            yield Static("", id="status")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Creer", id="create", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Annuler", id="cancel")
        yield Footer()

    def on_mount(self) -> None:
        targets = load_controller.load_targets(target_repository=self._container.target_repository)
        self._targets_by_index = dict(enumerate(targets))
        self.query_one(TargetPicker).load_targets(targets)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._selected_target = self._targets_by_index.get(event.option_index)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
        elif event.button.id == "create":
            self._create()

    def _resolve_target(self) -> tuple[str, str] | None:
        manual_value = self.query_one(TargetPicker).manual_value.strip()
        if manual_value:
            return manual_value, manual_value
        if self._selected_target is not None:
            return self._selected_target.id, self._selected_target.base_url
        return None

    def _create(self) -> None:
        status = self.query_one("#status", Static)
        name = self.query_one("#name", Input).value.strip()
        target = self._resolve_target()
        default_target_id = target[0] if target is not None else ""
        family = self.query_one("#family", Select).value
        level = self.query_one("#level", Select).value
        duration_input = self.query_one("#duration", Input).value
        max_error_input = self.query_one("#max-error-rate", Input).value

        if not name or not default_target_id:
            status.update("Nom et cible par defaut sont obligatoires.")
            return
        if not isinstance(family, TestFamily) or not isinstance(level, IntensityLevel):
            status.update("Choisissez une famille et une intensite.")
            return
        try:
            duration_minutes = int(duration_input)
            max_error_rate = float(max_error_input)
        except ValueError:
            status.update("Duree et taux d'erreur doivent etre numeriques.")
            return

        result = profile_controller.create(
            profile_repository=self._container.profile_repository,
            name=name,
            description=self.query_one("#description", Input).value,
            default_target_id=default_target_id,
            family=family,
            level=level,
            duration_minutes=duration_minutes,
            max_error_rate=max_error_rate,
        )
        if isinstance(result, Err):
            status.update(str(result.error))
            return
        self.dismiss()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit une saisie de formulaire en appel a
#   controllers/profile_controller.py::create().
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Aucune validation metier ici (deja dans domain/profiles/validation.py,
#   relayee via le Result retourne) : seule la presence/le type des champs
#   est verifie avant l'appel, pas leur validite metier.
# Ce qu'il ne contient PAS :
# - Aucune verification que default_target_id reference une cible
#   existante : coherent avec application/commands/create_profile.py, qui
#   documente deja cette absence comme deliberee en V1.
# Points cles :
# - _resolve_target() (2026-08-24, corrige) reprend EXACTEMENT le motif
#   de screens/request_panel.py : privilegie la saisie manuelle, sinon la
#   cible connue selectionnee dans TargetPicker. Avant ce correctif,
#   cet ecran ignorait completement la selection dans la liste connue
#   (seul TargetPicker.manual_value etait lu) — une incoherence relevee
#   en creusant le bug "champ cible toujours vide" du meme jour : cet
#   assistant etait le seul des 4 formulaires utilisant TargetPicker a ne
#   pas implementer on_option_list_option_selected().
# - default_target_id reste un identifiant BRUT (id de cible epinglee, ou
#   adresse manuelle reprise telle quelle) : coherent avec
#   application/commands/create_profile.py, qui documente deja l'absence
#   de verification d'existence comme deliberee en V1.
# - dismiss() sans argument signale juste "termine" a
#   screens/profiles.py, qui se recharge via son propre
#   on_screen_resume().
# Comment il sera utilise :
# - interfaces/tui/screens/profiles.py (bouton "Nouveau profil").
#---------------------------------------------------------------------->
