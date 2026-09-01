from omega_lib.terminal.models import RenderProfile

from omega_stress.interfaces.tui.controllers.theme_controller import (
    choose_theme,
    cycle_theme,
)
from tests.fixtures.fakes import FakeSettingsStore


def test_choose_theme_persists_the_selection():
    settings_store = FakeSettingsStore()

    status = choose_theme(
        "omega-neon", render_profile=RenderProfile.COMPLETE, settings_store=settings_store
    )

    assert status.theme_name == "omega-neon"
    assert settings_store.get("theme") == "omega-neon"


def test_cycle_theme_moves_to_the_next_entry():
    settings_store = FakeSettingsStore()

    status = cycle_theme(
        "omega-base",
        direction=1,
        render_profile=RenderProfile.COMPLETE,
        settings_store=settings_store,
    )

    assert status.theme_name == "omega-dark"


def test_cycle_theme_wraps_around():
    settings_store = FakeSettingsStore()

    status = cycle_theme(
        "omega-base",
        direction=-1,
        render_profile=RenderProfile.COMPLETE,
        settings_store=settings_store,
    )

    assert status.theme_name == "omega-minimal"


def test_cycle_theme_from_unknown_current_starts_at_the_beginning():
    settings_store = FakeSettingsStore()

    status = cycle_theme(
        "theme-inconnu",
        direction=1,
        render_profile=RenderProfile.COMPLETE,
        settings_store=settings_store,
    )

    assert status.theme_name == "omega-dark"
