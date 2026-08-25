from omega_stress.core.enums import RenderProfile
from omega_stress.domain.terminal.models import TerminalSignals
from omega_stress.domain.terminal.service import resolve_render_profile


def test_ghostty_large_terminal_is_complete():
    signals = TerminalSignals(family="ghostty", columns=200, rows=50)

    profile = resolve_render_profile(signals)

    assert profile.render_profile is RenderProfile.COMPLETE


def test_ghostty_in_small_tmux_pane_is_degraded_by_size():
    signals = TerminalSignals(family="ghostty", columns=70, rows=20)

    profile = resolve_render_profile(signals)

    assert profile.render_profile is RenderProfile.MONO


def test_unknown_family_falls_back_to_default_profile():
    signals = TerminalSignals(family="some-unknown-terminal", columns=200, rows=50)

    profile = resolve_render_profile(signals)

    assert profile.render_profile is RenderProfile.REDUCED


def test_linux_tty_is_always_mono_even_when_large():
    signals = TerminalSignals(family="linux-tty", columns=200, rows=50)

    profile = resolve_render_profile(signals)

    assert profile.render_profile is RenderProfile.MONO
