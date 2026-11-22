# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""« Mode charge distribuee » des ecrans de test (lot L3 + retours de l'auteur, 2026-11-21).

Sous « Mode securite » : une case « Mode charge distribuee » ; cochee, la ligne « Machines qui
chargent la cible » s'affiche, pre-cochee d'apres l'ecran Charge distribuee (machines qui
participent, « cette machine » decochee par defaut). Sans machine reliee, la case reste visible mais
grisee, avec l'explication : la liaison se fait uniquement dans omega-connect."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Static

from omega_stress.shared.i18n import _

Choice = tuple[tuple[str, ...], bool]
"""(identifiants des machines qui aident cochees, cette machine charge aussi)."""


class MachinesPicker(Vertical):
    DEFAULT_CSS = """
    MachinesPicker { height: auto; margin-top: 1; }
    MachinesPicker #machines-line { height: auto; }
    MachinesPicker #machines-line Checkbox { width: auto; }
    MachinesPicker #machines-block { height: auto; }
    """

    def __init__(
        self,
        machines: list[tuple[str, str]],
        open_screen: Callable[[], None],
        participating: Choice = ((), False),
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._machines = machines
        self._open_screen = open_screen
        self._participating = participating

    def compose(self) -> ComposeResult:
        yield Checkbox(
            _("Mode charge distribuée"),
            value=False,
            id="distributed-mode",
            disabled=not self._machines,
        )
        if not self._machines:
            yield Static(
                _(
                    "Aucune machine reliée : la liaison se fait uniquement dans omega-connect "
                    "(Synchronisation → Charge distribuée)."
                ),
                classes="omega-hint",
            )
        with Vertical(id="machines-block"):
            yield Static(_("Machines qui chargent la cible"), classes="omega-subtitle")
            chosen, local = self._participating
            with Horizontal(id="machines-line"):
                for index, (machine_id, name) in enumerate(self._machines):
                    yield Checkbox(name, value=machine_id in chosen, id=f"helper-{index}")
                yield Checkbox(_("cette machine"), value=local, id="helper-local")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Machines…"), id="machines-screen")

    def on_mount(self) -> None:
        self.query_one("#machines-block").display = False

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "distributed-mode":
            self.query_one("#machines-block").display = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "machines-screen":
            event.stop()
            self._open_screen()

    def choice(self) -> Choice | None:
        """None : test local (mode non coche, ou aucune machine qui aide cochee)."""
        if not self._machines or not self.query_one("#distributed-mode", Checkbox).value:
            return None
        chosen = tuple(
            machine_id
            for index, (machine_id, _name) in enumerate(self._machines)
            if self.query_one(f"#helper-{index}", Checkbox).value
        )
        if not chosen:
            return None
        return chosen, self.query_one("#helper-local", Checkbox).value
