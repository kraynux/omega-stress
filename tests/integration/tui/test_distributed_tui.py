# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Charge distribuee dans l'interface (lot L3, 2026-11-21) : ligne « Machines » des ecrans de test,
ecran « Charge distribuee », question d'accord. Jamais de SSH ni de sudo reels (services
factices)."""

from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import pytest
from omega_lib.terminal.models import TerminalSignals
from textual.widgets import Checkbox

from omega_stress.app.dependency_container import build_container
from omega_stress.interfaces.tui.app import OmegaStressApp
from omega_stress.interfaces.tui.screens.confirm import ConfirmScreen
from omega_stress.interfaces.tui.screens.distributed_screen import DistributedScreen
from omega_stress.interfaces.tui.screens.request_panel import RequestPanelScreen
from omega_stress.interfaces.tui.widgets.machines_picker import MachinesPicker
from tests.fixtures.fakes import FakeTerminalDetector


class FakeServices:
    def __init__(self, machines=(("m1", "B"), ("m2", "C")), password: bool = False) -> None:
        self._machines = [
            SimpleNamespace(machine_id=i, name=n, ssh=f"kr@{n}", path="/s") for i, n in machines
        ]
        self.password = password
        self.applied: list[bool] = []
        self.off: set[str] = set()
        self.local = False

    def machines(self):
        return self._machines

    def status(self, machine):
        return SimpleNamespace(
            machine=machine,
            reachable=True,
            linked=machine.name == "B",
            accept_all=False,
            max_requests_per_minute=180000,
        )

    def participating(self):
        return tuple(
            m.machine_id for m in self._machines if m.machine_id not in self.off
        ), self.local

    def set_participating(self, machine_id, on):
        (self.off.discard if on else self.off.add)(machine_id)

    def set_local(self, on):
        self.local = on

    def remove(self, machine_id):
        self._machines = [m for m in self._machines if m.machine_id != machine_id]
        return True

    def firewall_record(self):
        return {
            "backend": "omega-fire",
            "networks": ["192.168.1.0/24"],
            "port": 9650,
            "opened_at": "2026-11-21T22:46:00+01:00",
            "opened_by": "omega-connect",
            "rules": [
                {
                    "manager": "nftables",
                    "network": "192.168.1.0/24",
                    "state": "ajoutee",
                    "rule": "#12",
                }
            ],
        }

    def firewall_state(self):
        return SimpleNamespace(
            backend="omega-fire", opened=True, needs_opening=False, needs_omega_fire=False, port=9650
        )

    def can_ask_password(self):
        return self.password

    def authenticate(self):
        return True

    def firewall_apply(self, opening):
        self.applied.append(opening)
        return True, ""


def _container(tmp_path, services):
    base = build_container(var_dir=tmp_path)
    return dataclasses.replace(
        base,
        terminal_detector=FakeTerminalDetector(
            TerminalSignals(family="ghostty", columns=120, rows=40)
        ),
        distributed=services,
    )


async def _open_request_panel(app, pilot):
    await pilot.pause()
    await pilot.press("space")  # ecran d'accueil anime
    await pilot.pause()
    app.push_screen(RequestPanelScreen(container=app._container))  # type: ignore[attr-defined]
    await pilot.pause()


@pytest.mark.parametrize("machines", [(), (("m1", "B"), ("m2", "C"))])
async def test_mode_charge_distribuee(tmp_path, machines) -> None:
    app = OmegaStressApp(_container(tmp_path, FakeServices(machines)))
    async with app.run_test(size=(120, 90)) as pilot:
        await _open_request_panel(app, pilot)
        picker = app.screen.query_one(MachinesPicker)
        mode = picker.query_one("#distributed-mode", Checkbox)
        assert picker.display and picker.choice() is None
        if not machines:
            assert mode.disabled  # visible, grisee, avec l'explication omega-connect
            return
        assert not picker.query_one("#machines-block").display
        mode.value = True
        await pilot.pause()
        assert picker.query_one("#machines-block").display
        assert picker.choice() == (("m1", "m2"), False)  # pre-coche : machines oui, pilote non
        picker.query_one("#helper-local", Checkbox).value = True
        picker.query_one("#helper-1", Checkbox).value = False
        assert picker.choice() == (("m1",), True)
        picker.query_one("#helper-0", Checkbox).value = False
        assert picker.choice() is None  # aucune machine qui aide : test local


async def test_ecran_charge_distribuee(tmp_path) -> None:
    services = FakeServices()
    app = OmegaStressApp(_container(tmp_path, services))
    async with app.run_test(size=(120, 90)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # ecran d'accueil anime
        await pilot.pause()
        assert not app.screen.query("#quit")  # « Quitter » retire du menu (touches q / Echap)
        await pilot.click("#distributed")
        await pilot.pause()
        assert isinstance(app.screen, DistributedScreen)
        await app.workers.wait_for_complete()
        await pilot.pause()
        screen = app.screen
        assert screen.query_one("#distributed-machines").row_count == 3  # cette machine + B + C
        report = str(screen.query_one("#firewall-state").render())
        assert "omega-connect" in report and "#12" in report and "nftables" in report
        screen.action_toggle_row()  # ligne 0 : cette machine
        assert services.local is True
        screen.query_one("#distributed-machines").move_cursor(row=1)
        screen.action_toggle_row()
        assert services.participating() == (("m2",), True)
        assert app.screen.query_one("#close-frame").display
        await pilot.click(
            "#firewall-close"
        )  # sans terminal pour le mot de passe : refus, rien lance
        await pilot.pause()
        assert services.applied == []


async def test_question_d_accord(tmp_path) -> None:
    app = OmegaStressApp(_container(tmp_path, FakeServices()))
    async with app.run_test(size=(120, 90)) as pilot:
        await _open_request_panel(app, pilot)
        panel = app.screen
        answers: list[bool] = []

        async def ask() -> None:
            answers.append(await panel._approve("B", "https://cible.lan"))

        app.run_worker(ask())
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.click("#confirm")
        await pilot.pause()
        await app.workers.wait_for_complete()
        assert answers == [True]
