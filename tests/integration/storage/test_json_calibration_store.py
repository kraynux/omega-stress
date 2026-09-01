from datetime import datetime, timezone

from omega_stress.domain.calibration.models import (
    CalibrationEnvelope,
    CalibrationFingerprint,
    CalibrationResult,
    CalibrationStageResult,
)
from omega_stress.domain.calibration.service import compute_fingerprint_hash
from omega_stress.infrastructure.storage.files.json_calibration_store import JsonCalibrationStore

STARTED = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)


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


def _result(**overrides) -> CalibrationResult:
    defaults = dict(
        fingerprint=_fingerprint(),
        started_at=STARTED,
        duration_seconds=42.5,
        stages=(
            CalibrationStageResult(
                stage_id="calib_1",
                vu_target=25,
                rps_target=100,
                rps_achieved=98.0,
                error_rate=0.0,
                peak_cpu_percent_generator=12.0,
                peak_cpu_percent_global=15.0,
                memory_available_percent_min=80.0,
                is_healthy=True,
                stop_reason=None,
            ),
        ),
        envelope=CalibrationEnvelope(
            vu_safe=17,
            rps_safe=68,
            connections_safe=17,
            margin_applied=0.70,
            last_healthy_stage_id="calib_1",
            first_degraded_stage_id=None,
            confidence="faible",
        ),
        overall_stop_reason=None,
    )
    defaults.update(overrides)
    return CalibrationResult(**defaults)


def test_load_returns_none_when_never_calibrated(tmp_path):
    store = JsonCalibrationStore(tmp_path / "calibrations")

    assert store.load("unknown-hash") is None


def test_save_then_load_roundtrips(tmp_path):
    store = JsonCalibrationStore(tmp_path / "calibrations")
    result = _result()

    store.save(result)
    fetched = store.load(compute_fingerprint_hash(result.fingerprint))

    assert fetched == result


def test_save_creates_parent_directory_if_missing(tmp_path):
    calibrations_dir = tmp_path / "nested" / "calibrations"
    store = JsonCalibrationStore(calibrations_dir)

    store.save(_result())

    assert calibrations_dir.exists()


def test_result_without_envelope_roundtrips(tmp_path):
    # Un calibrage qui echoue des le premier palier reste persistable.
    store = JsonCalibrationStore(tmp_path / "calibrations")
    result = _result(envelope=None, overall_stop_reason="generator_cpu_sustained")

    store.save(result)
    fetched = store.load(compute_fingerprint_hash(result.fingerprint))

    assert fetched == result
    assert fetched.envelope is None


def test_save_overwrites_previous_result_for_the_same_fingerprint(tmp_path):
    store = JsonCalibrationStore(tmp_path / "calibrations")
    store.save(_result(duration_seconds=10.0))
    store.save(_result(duration_seconds=99.0))

    fetched = store.load(compute_fingerprint_hash(_fingerprint()))

    assert fetched.duration_seconds == 99.0
