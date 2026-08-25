import pytest

from omega_stress.core.capability import Capability
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import CapabilityStatus
from omega_stress.core.exceptions import CapabilityRegistryError


def test_register_and_get_roundtrip():
    registry = CapabilityRegistry()
    cap = Capability(name="terminal.color", status=CapabilityStatus.AVAILABLE)

    registry.register(cap)

    assert registry.get("terminal.color") == cap
    assert registry.status_of("terminal.color") == CapabilityStatus.AVAILABLE
    assert registry.is_usable("terminal.color") is True


def test_get_unknown_capability_raises():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.get("does.not.exist")


@pytest.mark.parametrize(
    ("status", "expected_usable"),
    [
        (CapabilityStatus.AVAILABLE, True),
        (CapabilityStatus.DEGRADED, True),
        (CapabilityStatus.MISSING, False),
        (CapabilityStatus.DISQUALIFIED, False),
    ],
)
def test_missing_or_disqualified_are_never_usable(status, expected_usable):
    registry = CapabilityRegistry()
    registry.register(Capability(name="system.fd", status=status))

    assert registry.is_usable("system.fd") is expected_usable


def test_all_returns_every_registered_capability():
    registry = CapabilityRegistry()
    registry.register(Capability(name="a", status=CapabilityStatus.AVAILABLE))
    registry.register(Capability(name="b", status=CapabilityStatus.MISSING))

    names = {cap.name for cap in registry.all()}

    assert names == {"a", "b"}
