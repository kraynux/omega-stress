from datetime import datetime, timezone

from omega_stress.application.pipeline.abort import abort_run
from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.errors import ThresholdExceededError
from omega_stress.domain.runs.models import IntervalSample, LoadRun

STARTED = datetime(2026, 8, 24, 10, 0, tzinfo=timezone.utc)
ABORTED_AT = datetime(2026, 8, 24, 10, 2, tzinfo=timezone.utc)


def test_abort_closes_run_with_auto_stopped_verdict():
    run = LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.HAUT,
        started_at=STARTED,
    )
    samples = (
        IntervalSample(
            at_second=1.0,
            observed_rate_per_minute=1000.0,
            p50_latency_ms=10.0,
            p95_latency_ms=20.0,
            p99_latency_ms=30.0,
            error_count=8,
            request_count=10,
        ),
    )

    result = abort_run(
        run, samples=samples, reason=ThresholdExceededError("seuil depasse"), now=ABORTED_AT
    )

    assert result.finished_at == ABORTED_AT
    assert result.result is not None
    assert result.result.verdict is RunVerdict.AUTO_STOPPED
    assert result.result.error_count == 8


def test_abort_records_the_reason_as_an_event():
    run = LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.HAUT,
        started_at=STARTED,
    )

    result = abort_run(
        run, samples=(), reason=ThresholdExceededError("taux d'erreur > 10%"), now=ABORTED_AT
    )

    assert result.result is not None
    assert len(result.result.events) == 1
    event = result.result.events[0]
    assert event.kind == "threshold_exceeded"
    assert event.message == "taux d'erreur > 10%"
    assert event.occurred_at == ABORTED_AT
