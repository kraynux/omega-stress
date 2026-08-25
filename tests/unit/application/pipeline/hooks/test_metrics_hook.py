from omega_stress.application.pipeline.hooks.metrics_hook import publish_sample
from omega_stress.domain.runs.models import IntervalSample
from tests.fixtures.fakes import FakeRunProgressNotifier


def test_publish_sample_forwards_to_notifier():
    notifier = FakeRunProgressNotifier()
    sample = IntervalSample(
        at_second=1.0,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
    )

    publish_sample("run-1", sample, notifier=notifier)

    assert notifier.notifications == [("run-1", sample)]
