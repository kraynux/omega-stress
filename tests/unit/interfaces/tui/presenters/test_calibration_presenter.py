from datetime import datetime, timezone

from omega_stress.core.enums import TestFamily
from omega_stress.domain.calibration.models import (
    CalibrationEnvelope,
    CalibrationFingerprint,
    CalibrationResult,
)
from omega_stress.interfaces.tui.presenters.calibration_presenter import (
    envelope_comparison_message,
)

STARTED = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)


def _fingerprint() -> CalibrationFingerprint:
    return CalibrationFingerprint(
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


def _result(envelope: CalibrationEnvelope | None) -> CalibrationResult:
    return CalibrationResult(
        fingerprint=_fingerprint(),
        started_at=STARTED,
        duration_seconds=42.0,
        stages=(),
        envelope=envelope,
        overall_stop_reason=None if envelope is not None else "generator_cpu_sustained",
    )


def _envelope(**overrides) -> CalibrationEnvelope:
    defaults = dict(
        vu_safe=140,
        rps_safe=700,
        connections_safe=140,
        margin_applied=0.70,
        last_healthy_stage_id="calib_3",
        first_degraded_stage_id=None,
        confidence="moyenne",
    )
    defaults.update(overrides)
    return CalibrationEnvelope(**defaults)


def test_no_result_recommends_calibrating():
    message = envelope_comparison_message(
        family=TestFamily.REQUEST, target_value=100.0, unit="req/s", result=None
    )

    assert "Aucun calibrage" in message
    assert "responsabilite" in message


def test_result_without_envelope_recommends_calibrating():
    message = envelope_comparison_message(
        family=TestFamily.CONNECTION, target_value=100.0, unit="connexions", result=_result(None)
    )

    assert "Aucun calibrage" in message


def test_connection_target_below_envelope_is_reported_as_such():
    result = _result(_envelope(connections_safe=200))

    message = envelope_comparison_message(
        family=TestFamily.CONNECTION, target_value=50.0, unit="connexions", result=result
    )

    assert "en dessous" in message
    assert "200 connexions" in message


def test_connection_target_above_envelope_is_flagged():
    result = _result(_envelope(connections_safe=200))

    message = envelope_comparison_message(
        family=TestFamily.CONNECTION, target_value=2000.0, unit="connexions", result=result
    )

    assert "AU-DESSUS" in message
    assert "responsabilite" in message


def test_request_target_compares_against_rps_safe_not_connections_safe():
    result = _result(_envelope(rps_safe=500, connections_safe=999))

    message = envelope_comparison_message(
        family=TestFamily.REQUEST, target_value=1000.0, unit="req/s", result=result
    )

    assert "500 req/s" in message
    assert "AU-DESSUS" in message
