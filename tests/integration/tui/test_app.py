import dataclasses

import pytest

from omega_stress.app.dependency_container import build_container
from omega_stress.core.enums import ExportFormat
from omega_stress.domain.terminal.models import TerminalSignals
from omega_stress.interfaces.tui.app import OmegaStressApp
from omega_stress.interfaces.tui.screens.export_dialog import ExportDialogScreen
from omega_stress.interfaces.tui.screens.help_screen import HelpScreen
from omega_stress.interfaces.tui.screens.history import HistoryScreen
from omega_stress.interfaces.tui.screens.home import HomeScreen
from omega_stress.interfaces.tui.screens.profiles import ProfilesScreen
from omega_stress.interfaces.tui.screens.request_panel import RequestPanelScreen
from omega_stress.interfaces.tui.screens.settings_screen import (
    DEFAULT_SCREENSHOT_DIR_KEY,
    SettingsScreen,
)
from omega_stress.interfaces.tui.screens.targets import TargetsScreen
from tests.fixtures.fakes import FakeTerminalDetector


@pytest.fixture
def container(tmp_path):
    base = build_container(var_dir=tmp_path)
    return dataclasses.replace(
        base,
        terminal_detector=FakeTerminalDetector(
            TerminalSignals(family="ghostty", columns=120, rows=40)
        ),
    )


async def test_app_boots_directly_to_home(container):
    """Regression : jusqu'au 2026-08-24, un ecran splash intermediaire
    s'affichait avant l'accueil (retire, voir screens/home.py)."""
    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        assert isinstance(app.screen, HomeScreen)


async def test_home_navigates_to_each_sub_screen(container):
    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        await pilot.click("#profiles")
        await pilot.pause()
        assert isinstance(app.screen, ProfilesScreen)

        await pilot.click("#back")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)

        await pilot.click("#request")
        await pilot.pause()
        assert isinstance(app.screen, RequestPanelScreen)

        await pilot.click("#back")
        await pilot.pause()

        await pilot.click("#history")
        await pilot.pause()
        assert isinstance(app.screen, HistoryScreen)

        await pilot.click("#back")
        await pilot.pause()

        await pilot.click("#settings")
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)

        await pilot.click("#back")
        await pilot.pause()

        await pilot.click("#targets")
        await pilot.pause()
        assert isinstance(app.screen, TargetsScreen)

        await pilot.click("#back")
        await pilot.pause()

        await pilot.click("#help")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)


async def test_theme_cycle_binding_changes_active_theme(container):
    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        initial_theme = app.theme
        await pilot.press("t")
        await pilot.pause()

        assert app.theme != initial_theme


async def test_pinning_a_target_makes_it_appear_in_the_known_targets_list(container):
    """Regression : avant le 2026-08-24, aucun ecran n'appelait jamais
    pin_target/unpin_target — le champ "Cible" des 3 ecrans de lancement
    restait donc toujours vide, quel que soit le nombre de profils crees."""
    from textual.widgets import Input

    from omega_stress.interfaces.tui.widgets.authorization_checkbox import AuthorizationCheckbox

    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        await pilot.click("#targets")
        await pilot.pause()
        screen = app.screen
        screen.query_one("#new-address", Input).value = "https://example.org"
        screen.query_one(AuthorizationCheckbox).value = True
        await pilot.pause()
        await pilot.click("#pin")
        await pilot.pause()
        assert "epinglee" in str(screen.query_one("#status").content)

        await pilot.click("#back")
        await pilot.pause()
        await pilot.click("#request")
        await pilot.pause()
        known = app.screen._targets_by_index
        assert any(t.base_url == "https://example.org/" and t.pinned for t in known.values())


async def test_settings_screenshot_dir_field_prefills_and_persists(container):
    from textual.widgets import Input

    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        await pilot.click("#settings")
        await pilot.pause()
        screen = app.screen
        field = screen.query_one("#default-screenshot-dir", Input)
        assert field.value == str(container.screenshot_dir)

        field.focus()
        await pilot.pause()
        field.value = "/tmp/mes-captures"
        await pilot.press("enter")
        await pilot.pause()

        assert container.settings_store.get(DEFAULT_SCREENSHOT_DIR_KEY) == "/tmp/mes-captures"


async def test_export_dialog_defaults_to_html_format(container):
    from textual.widgets import Select

    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        app.push_screen(ExportDialogScreen(container=container, run_id="unused"))
        await pilot.pause()

        assert app.screen.query_one("#format", Select).value == ExportFormat.HTML


async def test_unhandled_exception_is_caught_instead_of_crashing_the_app(container):
    """Filet de securite (ARCHITECTURE.md §5.4) : reproduit l'incident du
    2026-08-24 (une StorageError d'export fermait toute l'application) en
    simulant directement l'appel que Textual fait pour toute exception non
    prevue dans un worker."""
    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen, reintroduit le 2026-08-25
        await pilot.pause()

        app._handle_exception(RuntimeError("panne technique inattendue"))
        await pilot.pause()

        assert app.is_running
        notifications = list(app._notifications._notifications.values())
        assert len(notifications) == 1
        assert "panne technique inattendue" in notifications[0].message
