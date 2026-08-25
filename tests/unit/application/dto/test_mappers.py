from datetime import datetime, timezone

from omega_stress.application.dto.mappers import (
    pinned_target_to_dto,
    profile_to_dto,
    run_to_dto,
    target_to_dto,
    terminal_profile_to_dto,
)
from omega_stress.core.enums import IntensityLevel, RenderProfile, RunVerdict, TestFamily
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.runs.models import IntervalSample, LoadResult, LoadRun, RunEvent
from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from omega_stress.domain.terminal.models import TerminalProfile, TerminalSignals

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def test_profile_to_dto_flattens_nested_value_objects():
    profile = Profile(
        id="profile-1",
        name="Charge nominale",
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.1, max_p95_latency_ms=500),
        created_at=NOW,
    )

    dto = profile_to_dto(profile)

    assert dto.family == "request"
    assert dto.level == "bas"
    assert dto.duration_minutes == 1
    assert dto.max_error_rate == 0.1
    assert dto.created_at == NOW.isoformat()
    assert dto.frozen_at is None


def test_target_to_dto_reports_pinned_flag():
    target = Target(
        id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW
    )

    dto = target_to_dto(target, pinned=False)

    assert dto.pinned is False
    assert dto.base_url == "https://example.org/"


def test_pinned_target_to_dto_forces_pinned_true():
    target = Target(
        id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW
    )
    pinned = PinnedTarget(target=target, pinned_at=NOW, authorized_at=NOW)

    dto = pinned_target_to_dto(pinned)

    assert dto.pinned is True
    assert dto.id == "t-1"


def test_run_to_dto_ongoing_run_has_no_result_fields():
    run = LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=NOW,
    )

    dto = run_to_dto(run, target_address="https://example.org/")

    assert dto.finished_at is None
    assert dto.verdict is None
    assert dto.error_count is None


def test_run_to_dto_finished_run_includes_result_fields():
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
        profile_id="profile-1",
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=NOW,
        finished_at=NOW,
        result=result,
    )

    dto = run_to_dto(run, target_address="https://example.org/")

    assert dto.verdict == "success"
    assert dto.p95_latency_ms == 20.0
    assert dto.events == ()
    assert dto.sample_count == 0


def test_run_to_dto_flattens_events():
    result = LoadResult(
        verdict=RunVerdict.FAILED,
        requested_rate_per_minute=None,
        observed_rate_per_minute=None,
        p50_latency_ms=None,
        p95_latency_ms=None,
        p99_latency_ms=None,
        error_count=0,
        total_requests=0,
        events=(
            RunEvent(occurred_at=NOW, kind="runner_failure", message="cible injoignable"),
        ),
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

    dto = run_to_dto(run, target_address="https://example.org/")

    assert len(dto.events) == 1
    assert dto.events[0].occurred_at == NOW.isoformat()
    assert dto.events[0].kind == "runner_failure"
    assert dto.events[0].message == "cible injoignable"


def test_run_to_dto_counts_samples():
    result = LoadResult(
        verdict=RunVerdict.SUCCESS,
        requested_rate_per_minute=250,
        observed_rate_per_minute=248.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        total_requests=250,
        samples=(
            IntervalSample(
                at_second=0.0,
                observed_rate_per_minute=248.0,
                p50_latency_ms=10.0,
                p95_latency_ms=20.0,
                p99_latency_ms=30.0,
                error_count=0,
                request_count=4,
            ),
            IntervalSample(
                at_second=1.0,
                observed_rate_per_minute=248.0,
                p50_latency_ms=10.0,
                p95_latency_ms=20.0,
                p99_latency_ms=30.0,
                error_count=0,
                request_count=4,
            ),
        ),
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

    dto = run_to_dto(run, target_address="https://example.org/")

    assert dto.sample_count == 2


def test_terminal_profile_to_dto():
    signals = TerminalSignals(family="ghostty", columns=200, rows=50)
    profile = TerminalProfile(signals=signals, render_profile=RenderProfile.COMPLETE)

    dto = terminal_profile_to_dto(profile)

    assert dto.family == "ghostty"
    assert dto.render_profile == "complete"
