# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Charge distribuee dans les trois ecrans de test (lot L3, 2026-11-21) : machines reliees pour la
ligne « Machines », ecran « Charge distribuee », et question d'accord pendant un test (accord «
Demander »)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from omega_stress.interfaces.tui.screens.confirm import ConfirmScreen
from omega_stress.interfaces.tui.screens.distributed_screen import DistributedScreen
from omega_stress.shared.i18n import _

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer


class DistributedPanelMixin:
    _container: DependencyContainer
    app: Any

    def _helper_machines(self) -> list[tuple[str, str]]:
        services = getattr(self._container, "distributed", None)
        if services is None:
            return []
        try:
            return [(machine.machine_id, machine.name) for machine in services.machines()]
        except Exception:  # noqa: BLE001 - fichiers illisibles : pas de charge distribuee
            return []

    def _participating(self) -> tuple[tuple[str, ...], bool]:
        services = getattr(self._container, "distributed", None)
        try:
            return services.participating() if services is not None else ((), False)
        except Exception:  # noqa: BLE001
            return (), False

    def _open_distributed(self) -> None:
        services = getattr(self._container, "distributed", None)
        if services is not None:
            self.app.push_screen(DistributedScreen(services))

    async def _approve(self, machine: str, target: str) -> bool:
        """Accord « Demander » : le test attend la reponse ; « Oui » ecrit l'accord sur la machine
        qui aide."""
        answer = await self.app.push_screen_wait(
            ConfirmScreen(
                title=_("Accord demandé par {machine}").format(machine=machine),
                message=_(
                    "{machine} demande votre accord pour charger {target}. Autoriser cette cible "
                    "pour "
                    "toujours sur {machine} ?"
                ).format(machine=machine, target=target),
            )
        )
        return bool(answer)
