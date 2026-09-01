from omega_lib.terminal.models import RenderProfile, TerminalSignals

from omega_stress.application.commands.select_render_profile import select_render_profile
from tests.fixtures.fakes import FakeSettingsStore, FakeTerminalDetector


def test_automatic_profile_is_persisted():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=200, rows=50))
    store = FakeSettingsStore()

    dto = select_render_profile(terminal_detector=detector, settings_store=store)

    assert dto.render_profile == "complete"
    assert store.get("render_profile") == "complete"


def test_manual_override_wins_over_automatic_detection():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=200, rows=50))
    store = FakeSettingsStore()

    dto = select_render_profile(
        terminal_detector=detector, settings_store=store, manual_override=RenderProfile.MONO
    )

    assert dto.render_profile == "mono"
    assert store.get("render_profile") == "mono"
