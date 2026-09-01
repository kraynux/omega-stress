from omega_stress.domain.calibration.models import CalibrationFingerprint
from omega_stress.domain.calibration.service import compute_fingerprint_hash


def _fingerprint(**overrides) -> CalibrationFingerprint:
    defaults = dict(
        schema_version=1,
        engine_version="1.0.0",
        python_version="3.14.0",
        os_name="Linux",
        architecture="x86_64",
        logical_cpu_count=4,
        total_ram_mb=8192.0,
        open_files_soft_limit=1024,
        workers_mode="asyncio-single-process",
        scenario_id="payload-4k",
    )
    defaults.update(overrides)
    return CalibrationFingerprint(**defaults)


def test_hash_is_stable_for_the_same_fingerprint():
    fingerprint = _fingerprint()

    assert compute_fingerprint_hash(fingerprint) == compute_fingerprint_hash(fingerprint)


def test_hash_differs_when_fingerprint_differs():
    first = compute_fingerprint_hash(_fingerprint())
    second = compute_fingerprint_hash(_fingerprint(logical_cpu_count=8))

    assert first != second
