# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Charge distribuee (menu principal, sous Calibrage ; retours de l'auteur, 2026-11-21).

- Les machines reliees par omega-connect (la liaison se fait UNIQUEMENT la-bas) ; on coche celles
  qui participent aux prochains tests (Entree ou Espace), « cette machine » comprise (decochee par
  defaut). Le choix est garde (var/distributed/selection.json) et pre-coche le « Mode charge
  distribuee » des ecrans de test.
- « Supprimer la machine » : retire son acces chez ce pilote (omega-connect peut la relier de
  nouveau).
- Pare-feu de cette machine : compte rendu (gestionnaire, port, reseaux, qui a ouvert et quand,
  chaque regle avec son numero chez omega-fire) et « Ouvrir » / « Refermer » : un mot de passe sudo
  tape dans le vrai terminal (l'interface se met de cote), puis les commandes en sudo -n."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.confirm import ConfirmScreen
from omega_stress.shared.i18n import _

if TYPE_CHECKING:
    from omega_stress.infrastructure.distributed.services import DistributedServices, HelperStatus

LOCAL_ROW = "__local__"
SUDO_MESSAGE = _(
    "omega-stress — mot de passe sudo pour le pare-feu de cette machine (il ne s'affiche pas "
    "pendant la saisie). L'interface revient ensuite."
)
FIREWALL_WORDS = {
    "omega-fire": "omega-fire",
    "ufw": "ufw",
    "firewalld": "firewalld",
    "nftables": _("nftables seul"),
    "aucun": _("aucun pare-feu actif"),
}
STATE_WORDS = {
    "ajoutee": _("ajoutée"),
    "deja": _("déjà présente"),
    "ignoree": _("ignorée"),
    "echec": _("échec"),
    "retiree": _("retirée"),
    "absente": _("absente"),
}


def check_mark(on: bool) -> Text:
    """Case lisible de loin (retour de l'auteur : cases trop petites)."""
    return Text(" ✔ ", style="bold reverse green") if on else Text("   ", style="reverse dim")


class DistributedScreen(OmegaScreen):
    BINDINGS = [*OmegaScreen.BINDINGS, Binding("space", "toggle_row", _("Cocher"), show=False)]
    DEFAULT_CSS = """
    DistributedScreen #distributed-machines { height: auto; max-height: 16; margin-top: 1; }
    DistributedScreen #firewall-title { margin-top: 1; }
    """

    def __init__(self, services: DistributedServices) -> None:
        super().__init__()
        self._services = services
        self._statuses: list[HelperStatus] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("CHARGE DISTRIBUÉE"), classes="omega-title")
            yield Static(
                _(
                    "Cochez les machines qui participent aux prochains tests (Entrée ou Espace). "
                    "La liaison des machines se fait uniquement dans omega-connect "
                    "(Synchronisation → Charge distribuée)."
                ),
                classes="omega-hint",
            )
            yield Static("", id="distributed-status", classes="omega-hint")
            yield DataTable(id="distributed-machines")
            yield Static(
                _("Pare-feu de cette machine"), classes="omega-subtitle", id="firewall-title"
            )
            yield Static("", id="firewall-state")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame", id="open-frame"):
                    yield Button(_("Ouvrir le pare-feu"), id="firewall-open", variant="primary")
                with Container(classes="omega-btn-frame", id="close-frame"):
                    yield Button(_("Refermer le pare-feu"), id="firewall-close")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Supprimer la machine"), id="remove")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Actualiser"), id="refresh")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#distributed-machines", DataTable)
        table.cursor_type = "row"
        table.add_columns(
            _("Participe"), _("Machine"), _("Joignable"), _("Reliée"), _("Accord"), _("Débit max")
        )
        self._load()

    def _load(self) -> None:
        self.query_one("#distributed-status", Static).update(_("Lecture des machines…"))

        def collect() -> None:
            statuses = [self._services.status(machine) for machine in self._services.machines()]
            wall = self._services.firewall_state()
            record = self._services.firewall_record()
            self.app.call_from_thread(self._show, statuses, wall, record)

        self.run_worker(collect, thread=True, exclusive=True, group="distributed")

    def _show(self, statuses: list[HelperStatus], wall: Any, record: dict[str, Any]) -> None:
        self._statuses = statuses
        with contextlib.suppress(NoMatches):
            self._fill()
            self.query_one("#distributed-status", Static).update(
                _("{count} machine(s) reliée(s).").format(count=len(statuses))
                if statuses
                else _(
                    "Aucune machine reliée : reliez-en dans omega-connect (Synchronisation "
                    "→ Charge distribuée)."
                )
            )
            self.query_one("#firewall-state", Static).update(firewall_report(wall, record))
            self.query_one("#open-frame").display = bool(getattr(wall, "needs_opening", False))
            self.query_one("#close-frame").display = bool(getattr(wall, "opened", False))
            self.query_one("#remove", Button).disabled = not statuses

    def _fill(self) -> None:
        table = self.query_one("#distributed-machines", DataTable)
        row = table.cursor_row
        table.clear()
        chosen, local = self._services.participating()
        yes, no = _("oui"), _("non")
        table.add_row(check_mark(local), _("cette machine"), "—", "—", "—", "", key=LOCAL_ROW)
        for status in self._statuses:
            accord = ""
            if status.linked:
                accord = _("tout accepter") if status.accept_all else _("demander")
            rate = (
                f"{status.max_requests_per_minute} req/min"
                if status.max_requests_per_minute
                else ""
            )
            table.add_row(
                check_mark(status.machine.machine_id in chosen),
                status.machine.name,
                yes if status.reachable else no,
                yes if status.linked else no,
                accord,
                rate,
                key=status.machine.machine_id,
            )
        if row is not None and row < table.row_count:
            table.move_cursor(row=row)

    def _current(self) -> str | None:
        table = self.query_one("#distributed-machines", DataTable)
        if table.cursor_row is None or table.row_count == 0:
            return None
        if table.cursor_row == 0:
            return LOCAL_ROW
        return self._statuses[table.cursor_row - 1].machine.machine_id

    def action_toggle_row(self) -> None:
        current = self._current()
        if current is None:
            return
        chosen, local = self._services.participating()
        if current == LOCAL_ROW:
            self._services.set_local(not local)
        else:
            self._services.set_participating(current, current not in chosen)
        self._fill()

    def on_data_table_row_selected(self, _event: DataTable.RowSelected) -> None:
        self.action_toggle_row()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button.id
        if button == "back":
            self.action_back()
        elif button == "refresh":
            self._load()
        elif button == "remove":
            self._remove()
        elif button in ("firewall-open", "firewall-close"):
            self._firewall(button == "firewall-open")

    def _remove(self) -> None:
        current = self._current()
        status = next((s for s in self._statuses if s.machine.machine_id == current), None)
        if status is None:
            self.app.notify(_("Choisissez une machine dans la liste."))
            return

        def done(confirmed: bool | None) -> None:
            if confirmed:
                self._services.remove(status.machine.machine_id)
                self._load()

        self.app.push_screen(
            ConfirmScreen(
                title=_("Supprimer {machine} ?").format(machine=status.machine.name),
                message=_(
                    "Son accès à cette machine est retiré : elle ne participera plus aux tests. "
                    "omega-connect peut la relier de nouveau (Synchronisation → Charge "
                    "distribuée), et y retirer aussi la liaison (« Délier »)."
                ),
            ),
            done,
        )

    def _firewall(self, opening: bool) -> None:
        if not self._services.can_ask_password():
            self.app.notify(
                _("Un terminal est nécessaire pour le mot de passe (sudo)."), severity="error"
            )
            return
        with self.app.suspend():
            print("\n" + SUDO_MESSAGE, flush=True)
            authenticated = self._services.authenticate()
        if not authenticated:
            self.app.notify(
                _("Mot de passe refusé ou annulé : rien n'a été modifié."), severity="error"
            )
            return

        def apply() -> None:
            ok, detail = self._services.firewall_apply(opening)
            self.app.call_from_thread(self._applied, ok, detail)

        self.run_worker(apply, thread=True, exclusive=True, group="distributed")

    def _applied(self, ok: bool, detail: str) -> None:
        if ok:
            self.app.notify(_("Pare-feu mis à jour."))
        else:
            self.app.notify(
                _("Pare-feu : échec ({detail}).").format(detail=detail or "?"), severity="error"
            )
        self._load()


def firewall_report(wall: Any, record: dict[str, Any]) -> Text:
    """Compte rendu du pare-feu (retour de l'auteur : « qui a ouvert le port, quelle regle, quel
    pare-feu ou gestionnaire a fait l'operation »)."""
    backend = str(getattr(wall, "backend", "aucun"))
    opened = bool(getattr(wall, "opened", False))
    networks = ", ".join(str(n) for n in record.get("networks", ())) or "?"
    text = Text()
    text.append(
        _("Gestionnaire : {firewall} ; port {port}/tcp").format(
            firewall=FIREWALL_WORDS.get(backend, backend), port=getattr(wall, "port", "?")
        )
        + "\n"
    )
    if opened and record.get("opened_at"):
        line = _("Ouvert pour {networks} — par {who}, le {when}").format(
            networks=networks,
            who=record.get("opened_by", "?"),
            when=str(record.get("opened_at", "?")).replace("T", " ")[:16],
        )
        text.append(line + "\n", style="bold")
    elif opened:
        text.append(_("Ouvert pour {networks}").format(networks=networks) + "\n", style="bold")
    elif getattr(wall, "needs_opening", False):
        line = _("Port fermé : les machines qui aident ne peuvent pas joindre cette machine.")
        text.append(line + "\n", style="bold")
    elif getattr(wall, "needs_omega_fire", False):
        line = _(
            "nftables seul : installez omega-fire pour ouvrir le port d'omega-stress (sa "
            "configuration n'est jamais réécrite à la main)."
        )
        text.append(line + "\n")
    else:
        text.append(_("Rien à ouvrir.") + "\n")
    rules = record.get("rules") if opened else None
    if rules:
        text.append(_("Règles posées :") + "\n")
        for rule in rules:
            state = STATE_WORDS.get(str(rule.get("state", "")), str(rule.get("state", "")))
            detail = f" · {rule['rule']}" if rule.get("rule") else ""
            text.append(
                f"  {rule.get('manager', '?')} · {rule.get('network', '?')} · {state}{detail}\n"
            )
    elif opened:
        line = _("Détail des règles non enregistré (ouverture faite avant ce compte rendu).")
        text.append(line + "\n", style="dim")
    if record.get("closed_at"):
        line = _("Refermé par {who}, le {when}").format(
            who=record.get("closed_by", "?"),
            when=str(record.get("closed_at")).replace("T", " ")[:16],
        )
        text.append(line + "\n")
    return text
