from omega_stress.core.enums import CapabilityStatus
from omega_stress.infrastructure.probe.local_probe import (
    CPU_CAPABILITY,
    LOAD_CAPACITY_CAPABILITY,
    MEMORY_CAPABILITY,
    OPEN_FILES_CAPABILITY,
    LocalSystemProbe,
)


def test_probe_returns_four_capabilities():
    capabilities = LocalSystemProbe().probe()

    names = {c.name for c in capabilities}
    assert names == {
        CPU_CAPABILITY,
        MEMORY_CAPABILITY,
        OPEN_FILES_CAPABILITY,
        LOAD_CAPACITY_CAPABILITY,
    }


def test_all_capabilities_have_a_known_status():
    capabilities = LocalSystemProbe().probe()

    for capability in capabilities:
        assert capability.status in CapabilityStatus
        assert capability.detail
