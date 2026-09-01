from datetime import datetime, timezone

from omega_stress.core.enums import RunVerdict
from omega_stress.domain.runs.models import ErrorBreakdown, IntervalSample, RunEvent, SystemSnapshot
from omega_stress.domain.runs.service import aggregate_samples


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


def test_empty_samples_produce_none_metrics():
    result = aggregate_samples((), verdict=RunVerdict.FAILED, requested_rate_per_minute=None)

    assert result.observed_rate_per_minute is None
    assert result.total_requests == 0
    assert result.verdict is RunVerdict.FAILED


def test_events_default_to_empty():
    result = aggregate_samples(
        (_sample(),), verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250
    )

    assert result.events == ()


def test_events_are_relayed_even_without_samples():
    event = RunEvent(
        occurred_at=datetime(2026, 8, 24, tzinfo=timezone.utc),
        kind="runner_failure",
        message="cible injoignable",
    )

    result = aggregate_samples(
        (), verdict=RunVerdict.FAILED, requested_rate_per_minute=None, events=(event,)
    )

    assert result.events == (event,)


def test_events_are_relayed_with_samples():
    event = RunEvent(
        occurred_at=datetime(2026, 8, 24, tzinfo=timezone.utc),
        kind="threshold_exceeded",
        message="seuil depasse",
    )

    result = aggregate_samples(
        (_sample(),),
        verdict=RunVerdict.AUTO_STOPPED,
        requested_rate_per_minute=250,
        events=(event,),
    )

    assert result.events == (event,)


def test_samples_are_kept_on_the_result():
    samples = (_sample(at_second=0.0), _sample(at_second=1.0))

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.samples == samples


def test_samples_are_kept_empty_when_none_collected():
    result = aggregate_samples((), verdict=RunVerdict.FAILED, requested_rate_per_minute=None)

    assert result.samples == ()


def test_sums_requests_and_errors():
    samples = (
        _sample(request_count=10, error_count=1),
        _sample(request_count=20, error_count=2),
    )

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.total_requests == 30
    assert result.error_count == 3


def test_p95_p99_take_the_worst_observed_value():
    samples = (
        _sample(p95_latency_ms=20.0, p99_latency_ms=30.0),
        _sample(p95_latency_ms=80.0, p99_latency_ms=90.0),
    )

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.p95_latency_ms == 80.0
    assert result.p99_latency_ms == 90.0


def test_p50_and_rate_take_the_mean():
    samples = (
        _sample(p50_latency_ms=10.0, observed_rate_per_minute=200.0),
        _sample(p50_latency_ms=20.0, observed_rate_per_minute=300.0),
    )

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.p50_latency_ms == 15.0
    assert result.observed_rate_per_minute == 250.0


def test_empty_samples_produce_a_zeroed_error_breakdown_and_no_peaks():
    result = aggregate_samples((), verdict=RunVerdict.FAILED, requested_rate_per_minute=None)

    assert result.errors == ErrorBreakdown()
    assert result.peak_cpu_percent_generator is None
    assert result.peak_memory_rss_mb is None


def test_error_breakdown_is_summed_across_samples():
    samples = (
        _sample(errors=ErrorBreakdown(timeout=1, http_5xx=2)),
        _sample(errors=ErrorBreakdown(timeout=3, connection=1)),
    )

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.errors == ErrorBreakdown(timeout=4, connection=1, http_5xx=2)


def test_peak_cpu_and_memory_take_the_maximum_observed():
    samples = (
        _sample(system=SystemSnapshot(cpu_percent_generator=20.0, memory_rss_mb=50.0)),
        _sample(system=SystemSnapshot(cpu_percent_generator=75.0, memory_rss_mb=40.0)),
        _sample(system=None),
    )

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.peak_cpu_percent_generator == 75.0
    assert result.peak_memory_rss_mb == 50.0


def test_peaks_stay_none_when_no_sample_has_system_data():
    samples = (_sample(system=None), _sample(system=None))

    result = aggregate_samples(samples, verdict=RunVerdict.SUCCESS, requested_rate_per_minute=250)

    assert result.peak_cpu_percent_generator is None
    assert result.peak_memory_rss_mb is None
