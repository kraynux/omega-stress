import pytest

from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.load.models import Duration, RampStep, Thresholds


def test_thresholds_rejects_error_rate_out_of_bounds():
    with pytest.raises(ValidationError):
        Thresholds(max_error_rate=1.5)


def test_thresholds_rejects_non_positive_latency():
    with pytest.raises(ValidationError):
        Thresholds(max_error_rate=0.1, max_p95_latency_ms=0)


def test_thresholds_accepts_valid_values():
    thresholds = Thresholds(max_error_rate=0.05, max_p95_latency_ms=500)
    assert thresholds.max_error_rate == 0.05
    assert thresholds.max_p95_latency_ms == 500


def test_duration_for_level_rejects_disallowed_minutes():
    result = Duration.for_level(IntensityLevel.HAUT, 5)

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)


def test_duration_for_level_accepts_extended_when_authorized():
    result = Duration.for_level(IntensityLevel.HAUT, 5, extended_authorized=True)

    assert isinstance(result, Ok)
    assert result.value.minutes == 5


def test_ramp_step_rejects_ratio_out_of_bounds():
    with pytest.raises(ValidationError):
        RampStep(order=1, duration_minutes=1, start_ratio=-0.1, end_ratio=1.0)


def test_ramp_step_rejects_non_positive_duration():
    with pytest.raises(ValidationError):
        RampStep(order=1, duration_minutes=0, start_ratio=0.0, end_ratio=1.0)
