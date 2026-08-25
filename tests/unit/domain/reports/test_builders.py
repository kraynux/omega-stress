from datetime import datetime, timezone

import pytest

from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.reports.builders import build_report_content
from omega_stress.domain.runs.models import LoadResult, LoadRun, RunEvent

STARTED = datetime(2026, 8, 23, 10, 0, tzinfo=timezone.utc)
FINISHED = datetime(2026, 8, 23, 10, 3, tzinfo=timezone.utc)


def _result(**overrides):
    defaults = dict(
        verdict=RunVerdict.SUCCESS,
        requested_rate_per_minute=250,
        observed_rate_per_minute=248.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        total_requests=750,
    )
    defaults.update(overrides)
    return LoadResult(**defaults)


def _run(**overrides):
    defaults = dict(
        id="run-1",
        profile_id="profile-1",
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
        finished_at=FINISHED,
        result=_result(),
    )
    defaults.update(overrides)
    return LoadRun(**defaults)


def test_raises_for_unfinished_run():
    unfinished = _run(finished_at=None, result=None)

    with pytest.raises(ValueError):
        build_report_content(unfinished, target_address="https://example.org/")


def test_builds_summary_with_computed_duration():
    content = build_report_content(_run(), target_address="https://example.org/")

    assert content.summary.run_id == "run-1"
    assert content.summary.duration_minutes == pytest.approx(3.0)


def test_success_verdict_has_no_error_recommendation():
    content = build_report_content(_run(), target_address="https://example.org/")

    assert content.diagnostic.verdict is RunVerdict.SUCCESS
    assert content.diagnostic.recommendations == ()


def test_errors_produce_a_recommendation():
    run_with_errors = _run(result=_result(error_count=5, total_requests=750))

    content = build_report_content(run_with_errors, target_address="https://example.org/")

    assert any("erreur" in rec for rec in content.diagnostic.recommendations)


def test_significant_rate_gap_flags_local_bottleneck():
    degraded = _run(
        result=_result(requested_rate_per_minute=1000, observed_rate_per_minute=500.0)
    )

    content = build_report_content(degraded, target_address="https://example.org/")

    assert any("goulot d'etranglement" in rec for rec in content.diagnostic.recommendations)


def test_minor_rate_gap_does_not_flag_bottleneck():
    fine = _run(result=_result(requested_rate_per_minute=1000, observed_rate_per_minute=950.0))

    content = build_report_content(fine, target_address="https://example.org/")

    assert content.diagnostic.recommendations == ()


def test_run_events_are_surfaced_as_recommendations():
    failed = _run(
        finished_at=FINISHED,
        result=_result(
            verdict=RunVerdict.FAILED,
            error_count=0,
            events=(
                RunEvent(
                    occurred_at=FINISHED, kind="runner_failure", message="cible injoignable"
                ),
            ),
        ),
    )

    content = build_report_content(failed, target_address="https://example.org/")

    assert content.diagnostic.recommendations[0] == "cible injoignable"
