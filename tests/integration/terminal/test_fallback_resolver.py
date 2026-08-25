from omega_stress.infrastructure.terminal.fallback_resolver import resolve_family
from omega_stress.infrastructure.terminal.raw_capabilities import RawTerminalSignals


def _signals(**overrides) -> RawTerminalSignals:
    defaults = dict(
        term="xterm-256color",
        term_program="",
        colorterm="",
        is_ssh=False,
        columns=120,
        rows=32,
        has_terminator_marker=False,
        has_konsole_marker=False,
        has_gnome_terminal_marker=False,
    )
    defaults.update(overrides)
    return RawTerminalSignals(**defaults)


def test_known_term_program_is_recognized():
    assert resolve_family(_signals(term_program="ghostty")) == "ghostty"


def test_gnome_terminal_recognized_from_term():
    assert resolve_family(_signals(term="gnome-256color")) == "gnome-terminal"


def test_terminator_recognized_via_marker_despite_generic_xterm_term():
    """Regression (2026-08-25) : Terminator laisse TERM a sa valeur de
    compatibilite par defaut ("xterm-256color") et ne renseigne jamais
    TERM_PROGRAM — reproduit sur un Terminator reel, resolvait avant ce
    correctif en famille "xterm" (RenderProfile.REDUCED) au lieu de
    "terminator" (RenderProfile.STANDARD)."""
    result = resolve_family(
        _signals(term="xterm-256color", term_program="", has_terminator_marker=True)
    )
    assert result == "terminator"


def test_konsole_recognized_via_marker_despite_generic_xterm_term():
    result = resolve_family(
        _signals(term="xterm-256color", term_program="", has_konsole_marker=True)
    )
    assert result == "konsole"


def test_gnome_terminal_recognized_via_marker_despite_generic_xterm_term():
    result = resolve_family(
        _signals(term="xterm-256color", term_program="", has_gnome_terminal_marker=True)
    )
    assert result == "gnome-terminal"


def test_linux_tty_recognized():
    assert resolve_family(_signals(term="linux")) == "linux-tty"


def test_generic_xterm_fallback():
    assert resolve_family(_signals(term="xterm-256color")) == "xterm"


def test_ssh_modern_detected_via_colorterm():
    result = resolve_family(_signals(is_ssh=True, colorterm="truecolor", term="xterm-256color"))
    assert result == "ssh-modern"


def test_ssh_legacy_when_no_modern_signal():
    result = resolve_family(_signals(is_ssh=True, colorterm="", term="xterm"))
    assert result == "ssh-legacy"


def test_unknown_term_falls_back_to_raw_value():
    assert resolve_family(_signals(term="some-weird-term")) == "some-weird-term"
