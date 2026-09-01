from omega_stress.application.pipeline.guards.threshold_guard import (
    check_sliding_window,
    check_threshold,
)
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.runs.models import ErrorBreakdown, IntervalSample


def _sample(**overrides) -> IntervalSample:
    defaults = dict(
        at_second=1.0,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
    )
    defaults.update(overrides)
    return IntervalSample(**defaults)


def test_passes_within_bounds():
    thresholds = Thresholds(max_error_rate=0.1, max_p95_latency_ms=500)

    result = check_threshold(_sample(), thresholds=thresholds)

    assert isinstance(result, Ok)


def test_flags_error_rate_breach():
    thresholds = Thresholds(max_error_rate=0.1)

    result = check_threshold(_sample(error_count=5, request_count=10), thresholds=thresholds)

    assert isinstance(result, Err)


def test_no_division_by_zero_when_no_requests():
    thresholds = Thresholds(max_error_rate=0.1)

    result = check_threshold(_sample(error_count=0, request_count=0), thresholds=thresholds)

    assert isinstance(result, Ok)


def test_check_sliding_window_empty_history_is_ok():
    result = check_sliding_window([])

    assert isinstance(result, Ok)


def test_check_sliding_window_flags_breach_using_last_sample_as_now_second():
    samples = [
        _sample(at_second=5.0, request_count=40, errors=ErrorBreakdown(http_5xx=8)),
    ]

    result = check_sliding_window(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "window_http_5xx_rate_exceeded"
