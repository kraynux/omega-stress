from omega_stress.application.pipeline.degraded_mode import is_local_bottleneck
from omega_stress.domain.runs.models import IntervalSample


def _sample(observed_rate: float) -> IntervalSample:
    return IntervalSample(
        at_second=1.0,
        observed_rate_per_minute=observed_rate,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
    )


def test_no_bottleneck_when_no_requested_rate():
    assert is_local_bottleneck(_sample(100.0), requested_rate_per_minute=None) is False


def test_no_bottleneck_when_observed_close_to_requested():
    assert is_local_bottleneck(_sample(950.0), requested_rate_per_minute=1000) is False


def test_bottleneck_when_observed_significantly_below_requested():
    assert is_local_bottleneck(_sample(500.0), requested_rate_per_minute=1000) is True
