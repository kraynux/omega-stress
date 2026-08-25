from datetime import datetime, timezone

from omega_stress.application.pipeline.hooks.audit_hook import (
    emit_authorization_denied,
    emit_run_finished,
    emit_run_started,
)
from omega_stress.core.audit import AuditEvent
from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.runs.models import LoadResult, LoadRun

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _sink_collector():
    events: list[AuditEvent] = []
    return events, events.append


def test_emit_run_started_marks_authorized():
    events, sink = _sink_collector()
    run = LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=NOW,
    )

    emit_run_started(run, sink=sink)

    assert events[0].action == "run_started"
    assert events[0].authorized is True


def test_emit_run_finished_reports_verdict():
    events, sink = _sink_collector()
    result = LoadResult(
        verdict=RunVerdict.SUCCESS,
        requested_rate_per_minute=250,
        observed_rate_per_minute=248.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        total_requests=250,
    )
    run = LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=NOW,
        finished_at=NOW,
        result=result,
    )

    emit_run_finished(run, sink=sink)

    assert events[0].outcome == "success"


def test_emit_authorization_denied_marks_unauthorized():
    events, sink = _sink_collector()

    emit_authorization_denied("t-1", sink=sink)

    assert events[0].authorized is False
