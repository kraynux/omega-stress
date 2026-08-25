from omega_stress.core.enums import RenderProfile
from omega_stress.domain.terminal.models import TerminalSignals
from omega_stress.interfaces.tui.controllers.render_profile_controller import (
    apply_render_profile,
)
from tests.fixtures.fakes import FakeSettingsStore, FakeTerminalDetector


def test_auto_mode_uses_the_detected_profile():
    detector = FakeTerminalDetector(TerminalSignals(family="linux-tty", columns=80, rows=24))
    settings_store = FakeSettingsStore()

    status = apply_render_profile(terminal_detector=detector, settings_store=settings_store)

    assert status.render_profile == "mono"
    assert settings_store.get("render_profile") == "mono"


def test_manual_override_wins_over_auto_detection():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=120, rows=40))
    settings_store = FakeSettingsStore()

    status = apply_render_profile(
        terminal_detector=detector,
        settings_store=settings_store,
        manual_override=RenderProfile.REDUCED,
    )

    assert status.render_profile == "reduced"
    assert settings_store.get("render_profile") == "reduced"
