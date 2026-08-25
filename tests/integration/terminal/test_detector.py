from omega_stress.infrastructure.terminal.detector import SystemTerminalDetector


def test_detect_returns_signals_with_positive_size(monkeypatch):
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("SSH_CLIENT", raising=False)
    monkeypatch.delenv("SSH_CONNECTION", raising=False)

    signals = SystemTerminalDetector().detect()

    assert signals.columns > 0
    assert signals.rows > 0
    assert isinstance(signals.family, str) and signals.family
    assert signals.is_ssh is False


def test_detect_flags_ssh_session(monkeypatch):
    monkeypatch.setenv("SSH_CLIENT", "1.2.3.4 1 22")

    signals = SystemTerminalDetector().detect()

    assert signals.is_ssh is True
