from omega_stress.application.pipeline.guards.resource_guard import check_generator_resources
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import IntervalSample, SystemSnapshot


def _sample(at_second: float, system: SystemSnapshot | None) -> IntervalSample:
    return IntervalSample(
        at_second=at_second,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
        system=system,
    )


def test_empty_history_is_ok():
    assert isinstance(check_generator_resources([]), Ok)


def test_missing_latest_snapshot_is_ok():
    result = check_generator_resources([_sample(1.0, None)])

    assert isinstance(result, Ok)


def test_flags_sustained_high_cpu():
    # cpu_percent_global doit AUSSI etre sature (2026-09-01, second
    # correctif : le CPU generateur seul ne suffit plus, voir domain/load/
    # policies.py::GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_PERCENT).
    samples = [
        _sample(float(i), SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0))
        for i in range(1, 4)
    ]

    result = check_generator_resources(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "generator_cpu_exceeded"


def test_flags_low_available_memory():
    result = check_generator_resources([_sample(1.0, SystemSnapshot(memory_available_percent=5.0))])

    assert isinstance(result, Err)
    assert result.error.signal == "generator_memory_exceeded"


def test_flags_open_files_ratio_breach():
    result = check_generator_resources(
        [_sample(1.0, SystemSnapshot(open_files=900, open_files_soft_limit=1000))]
    )

    assert isinstance(result, Err)
    assert result.error.signal == "generator_fds_exceeded"
