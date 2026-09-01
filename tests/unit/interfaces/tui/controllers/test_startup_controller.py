from omega_lib.terminal.models import TerminalSignals

from omega_stress.interfaces.tui.controllers.startup_controller import (
    resolve_startup_state,
)
from tests.fixtures.fakes import FakeSettingsStore, FakeTerminalDetector


def test_first_launch_resolves_default_theme_and_auto_render_profile():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=120, rows=40))
    settings_store = FakeSettingsStore()

    state = resolve_startup_state(terminal_detector=detector, settings_store=settings_store)

    assert state.theme.theme_name == "omega-base"
    assert state.terminal.render_profile == "complete"
    assert settings_store.get("theme") == "omega-base"


def test_persisted_theme_is_reapplied():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=120, rows=40))
    settings_store = FakeSettingsStore({"theme": "omega-neon"})

    state = resolve_startup_state(terminal_detector=detector, settings_store=settings_store)

    assert state.theme.theme_name == "omega-neon"
    assert state.theme.fell_back_from is None


def test_unknown_persisted_theme_falls_back_and_is_re_persisted():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=120, rows=40))
    settings_store = FakeSettingsStore({"theme": "theme-inexistant"})

    state = resolve_startup_state(terminal_detector=detector, settings_store=settings_store)

    assert state.theme.theme_name == "omega-base"
    assert state.theme.fell_back_from == "theme-inexistant"
    assert settings_store.get("theme") == "omega-base"
