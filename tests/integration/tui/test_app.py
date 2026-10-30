import dataclasses
from datetime import datetime, timezone

import pytest
from omega_lib.terminal.models import TerminalSignals

from omega_stress.app.dependency_container import build_container
from omega_stress.application.commands.create_profile import create_profile
from omega_stress.application.commands.freeze_profile import freeze_profile
from omega_stress.application.commands.pin_target import pin_target
from omega_stress.core.enums import ExportFormat, IntensityLevel, TestFamily
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
from omega_stress.interfaces.tui.widgets.target_picker import TargetPicker
from omega_stress.shared.ids import new_id
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
        assert "épinglée" in str(screen.query_one("#status").content)

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


async def test_target_picker_hides_on_profile_selection_and_reappears_on_clear(container):
    """Regression 2026-09-27 (retour utilisateur) : le champ cible doit
    disparaitre des qu'un profil fige est selectionne (il porte deja sa
    propre cible par defaut), et redevenir visible si le profil est
    efface — jusqu'a ce correctif, aucun ecran ne masquait jamais le
    picker, quel que soit le profil choisi."""
    from textual.widgets import Select

    now = datetime.now(timezone.utc)
    pinned = pin_target(
        target_repository=container.target_repository,
        id_factory=new_id,
        now=now,
        raw_address="https://example.org",
        authorization_confirmed=True,
    )
    assert not hasattr(pinned, "error"), pinned

    created = create_profile(
        profile_repository=container.profile_repository,
        id_factory=new_id,
        now=now,
        name="Profil requetes",
        description="",
        default_target_id=pinned.value.id,
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration_minutes=1,
        max_error_rate=0.5,
    )
    frozen = freeze_profile(created.value.id, profile_repository=container.profile_repository, now=now)

    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 80)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss SplashScreen
        await pilot.pause()

        await pilot.click("#request")
        await pilot.pause()
        screen = app.screen
        picker = screen.query_one(TargetPicker)
        assert picker.display is True

        screen.query_one("#profile", Select).value = frozen.value
        await pilot.pause()
        assert picker.display is False
        assert frozen.value.name in str(screen.query_one("#target-hint").content)

        screen.query_one("#profile", Select).clear()
        await pilot.pause()
        assert picker.display is True
        assert str(screen.query_one("#target-hint").content) == ""


async def test_target_picker_content_is_actually_painted_not_just_sized(container):
    """Regression 2026-09-27 (bug reel rapporte, confirme par capture
    d'ecran reelle) : TargetPicker(Vertical) heritait de height:1fr +
    overflow:hidden (textual.containers.Vertical.DEFAULT_CSS) sans
    jamais etre corrige — meme famille de cause que widgets/
    run_progress.py::RunProgress (voir son INFO DEV, correctif du
    2026-08-25). Widget.size/.region rapportaient des hauteurs NON
    NULLES avant ce correctif (voir widgets/target_picker.py, INFO DEV)
    alors que le contenu reel restait totalement decoupe/invisible : ce
    test verifie donc le rendu PEINT (export_screenshot(), jamais
    Widget.size seul, qui aurait laisse passer la regression)."""
    now = datetime.now(timezone.utc)
    pin_target(
        target_repository=container.target_repository,
        id_factory=new_id,
        now=now,
        raw_address="https://example.org",
        authorization_confirmed=True,
    )

    app = OmegaStressApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        await pilot.press("space")
        await pilot.pause()
        await pilot.click("#connection")
        await pilot.pause()

        svg = app.export_screenshot()
        assert "example.org" in svg
        assert "saisir" in svg
