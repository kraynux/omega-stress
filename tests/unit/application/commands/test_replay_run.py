from datetime import datetime, timezone

from omega_stress.application.commands.replay_run import replay_run
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.runs.models import IntervalSample, LoadRun
from omega_stress.domain.targets.models import Target, TargetAddress
from tests.fixtures.fakes import (
    FakeLoadRunner,
    FakeProfileRepository,
    FakeRunProgressNotifier,
    FakeRunRepository,
    FakeTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _profile() -> Profile:
    return Profile(
        id="profile-1",
        name="Charge nominale",
        description="",
        default_target_id="t-other",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.5),
        created_at=NOW,
        frozen=True,
        frozen_at=NOW,
    )


def _target() -> Target:
    return Target(
        id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW
    )


def _sample() -> IntervalSample:
    return IntervalSample(
        at_second=1.0,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
    )


def _repos_with_replayable_run():
    run_repository = FakeRunRepository()
    profile_repository = FakeProfileRepository()
    target_repository = FakeTargetRepository()

    profile_repository.save(_profile())
    target_repository.save_recent(_target())
    run_repository.save(
        LoadRun(
            id="run-1",
            profile_id="profile-1",
            target_id="t-1",
            family=TestFamily.REQUEST,
            level=IntensityLevel.BAS,
            started_at=NOW,
            finished_at=NOW,
        )
    )
    return run_repository, profile_repository, target_repository


async def test_replay_launches_a_new_run_against_the_original_target():
    run_repository, profile_repository, target_repository = _repos_with_replayable_run()

    result = await replay_run(
        "run-1",
        run_repository=run_repository,
        profile_repository=profile_repository,
        target_repository=target_repository,
        load_runner=FakeLoadRunner([_sample()]),
        run_progress_notifier=FakeRunProgressNotifier(),
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "new-id",
        explicit_confirmation=True,
        precheck_validated=False,
        now=NOW,
    )

    assert isinstance(result, Ok)
    assert result.value.target_id == "t-1"  # cible originale, pas default_target_id du profil


async def test_replay_rejects_unknown_run():
    run_repository, profile_repository, target_repository = _repos_with_replayable_run()

    result = await replay_run(
        "does-not-exist",
        run_repository=run_repository,
        profile_repository=profile_repository,
        target_repository=target_repository,
        load_runner=FakeLoadRunner([_sample()]),
        run_progress_notifier=FakeRunProgressNotifier(),
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "new-id",
        explicit_confirmation=True,
        precheck_validated=False,
        now=NOW,
    )

    assert isinstance(result, Err)


async def test_replay_rejects_run_without_profile():
    run_repository, profile_repository, target_repository = _repos_with_replayable_run()
    run_repository.save(
        LoadRun(
            id="run-manual",
            profile_id=None,
            target_id="t-1",
            family=TestFamily.REQUEST,
            level=IntensityLevel.BAS,
            started_at=NOW,
            finished_at=NOW,
        )
    )

    result = await replay_run(
        "run-manual",
        run_repository=run_repository,
        profile_repository=profile_repository,
        target_repository=target_repository,
        load_runner=FakeLoadRunner([_sample()]),
        run_progress_notifier=FakeRunProgressNotifier(),
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "new-id",
        explicit_confirmation=True,
        precheck_validated=False,
        now=NOW,
    )

    assert isinstance(result, Err)
