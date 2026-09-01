from omega_stress.infrastructure.runner.async_worker import RequestOutcome
from omega_stress.infrastructure.runner.result_parser import parse_interval


def test_empty_outcomes_produce_zeroed_sample():
    sample = parse_interval(0.0, [])

    assert sample.request_count == 0
    assert sample.error_count == 0
    assert sample.observed_rate_per_minute == 0.0


def test_counts_and_rate_extrapolated_to_per_minute():
    outcomes = [RequestOutcome(latency_ms=10.0, success=True) for _ in range(5)]

    sample = parse_interval(0.0, outcomes)

    assert sample.request_count == 5
    assert sample.observed_rate_per_minute == 300.0  # 5 req/s * 60


def test_error_count_reflects_failed_outcomes():
    outcomes = [
        RequestOutcome(latency_ms=10.0, success=True),
        RequestOutcome(latency_ms=10.0, success=False),
        RequestOutcome(latency_ms=10.0, success=False),
    ]

    sample = parse_interval(0.0, outcomes)

    assert sample.error_count == 2
    assert sample.request_count == 3


def test_errors_broken_down_by_category():
    outcomes = [
        RequestOutcome(latency_ms=10.0, success=True),
        RequestOutcome(latency_ms=10.0, success=False, error_category="timeout"),
        RequestOutcome(latency_ms=10.0, success=False, error_category="timeout"),
        RequestOutcome(latency_ms=10.0, success=False, error_category="connection"),
        RequestOutcome(latency_ms=10.0, success=False, error_category="http_4xx"),
        RequestOutcome(latency_ms=10.0, success=False, error_category="http_5xx"),
    ]

    sample = parse_interval(0.0, outcomes)

    assert sample.errors.timeout == 2
    assert sample.errors.connection == 1
    assert sample.errors.http_4xx == 1
    assert sample.errors.http_5xx == 1
    assert sample.errors.other == 0
    assert sample.errors.total == sample.error_count


def test_unrecognized_error_category_falls_back_to_other():
    outcomes = [
        RequestOutcome(latency_ms=10.0, success=False, error_category="unknown_future_kind")
    ]

    sample = parse_interval(0.0, outcomes)

    assert sample.errors.other == 1
    assert sample.errors.total == 1


def test_percentiles_use_nearest_rank_on_sorted_latencies():
    # 100 valeurs 0.0..99.0 : index nearest-rank pour 0.50/0.95/0.99 avec
    # arrondi banquier de Python (round(49.5) == 50, round(94.05) == 94,
    # round(98.01) == 98) donne respectivement les rangs 50/94/98.
    outcomes = [RequestOutcome(latency_ms=float(i), success=True) for i in range(100)]

    sample = parse_interval(0.0, outcomes)

    assert sample.p50_latency_ms == 50.0
    assert sample.p95_latency_ms == 94.0
    assert sample.p99_latency_ms == 98.0
