from omega_stress.application.queries.detect_terminal import detect_terminal
from omega_stress.domain.terminal.models import TerminalSignals
from tests.fixtures.fakes import FakeTerminalDetector


def test_detect_terminal_resolves_render_profile():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=200, rows=50))

    dto = detect_terminal(terminal_detector=detector)

    assert dto.family == "ghostty"
    assert dto.render_profile == "complete"


def test_detect_terminal_degrades_for_small_size():
    detector = FakeTerminalDetector(TerminalSignals(family="ghostty", columns=60, rows=15))

    dto = detect_terminal(terminal_detector=detector)

    assert dto.render_profile == "mono"
