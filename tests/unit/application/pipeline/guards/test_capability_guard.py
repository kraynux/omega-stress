import pytest

from omega_stress.application.exceptions import CapabilityUnavailableError
from omega_stress.application.pipeline.guards.capability_guard import check_capability
from omega_stress.core.capability import Capability
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import CapabilityStatus
from omega_stress.core.exceptions import CapabilityRegistryError
from omega_stress.core.results import Err, Ok


def test_available_capability_passes():
    registry = CapabilityRegistry()
    registry.register(Capability(name="system.fd", status=CapabilityStatus.AVAILABLE))

    result = check_capability("system.fd", capability_registry=registry)

    assert isinstance(result, Ok)


def test_missing_capability_is_denied():
    registry = CapabilityRegistry()
    registry.register(Capability(name="system.fd", status=CapabilityStatus.MISSING))

    result = check_capability("system.fd", capability_registry=registry)

    assert isinstance(result, Err)
    assert isinstance(result.error, CapabilityUnavailableError)


def test_unknown_capability_raises_registry_error():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        check_capability("does.not.exist", capability_registry=registry)
