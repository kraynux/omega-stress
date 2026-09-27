from datetime import datetime, timezone

from omega_stress.application.commands.run_connection_load import run_connection_load
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Ok
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.runs.models import IntervalSample
from tests.fixtures.fakes import (
    FakeLoadRunner,
    FakeProfileRepository,
    FakeRunProgressNotifier,
    FakeRunRepository,
    FakeTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)

_SAMPLE = IntervalSample(
    at_second=1.0,
    observed_rate_per_minute=0.0,
    p50_latency_ms=10.0,
    p95_latency_ms=20.0,
    p99_latency_ms=30.0,
    error_count=0,
    request_count=0,
)


def _frozen_profile() -> Profile:
    return Profile(
        id="prof-1",
        name="Profil bas",
        description="",
        default_target_id="t-1",
        family=TestFamily.CONNECTION,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.5),
        created_at=NOW,
        frozen=True,
        frozen_at=NOW,
    )


async def test_profile_customized_true_when_error_rate_diverges():
    profile_repository = FakeProfileRepository()
    profile_repository.save(_frozen_profile())
    run_repository = FakeRunRepository()

    result = await run_connection_load(
        target_id="t-1",
        target_url="https://example.org/",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.9),  # diverge du profil (0.5)
        explicit_confirmation=True,
        precheck_validated=False,
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([_SAMPLE]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=run_repository,
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "id-1",
        now=lambda: NOW,
        profile_id="prof-1",
        profile_repository=profile_repository,
    )

    assert isinstance(result, Ok)
    assert result.value.profile_customized is True
    saved = run_repository.get(result.value.id)
    assert saved is not None
    assert saved.profile_customized is True


async def test_profile_customized_false_when_criteria_match_profile():
    profile_repository = FakeProfileRepository()
    profile_repository.save(_frozen_profile())
    run_repository = FakeRunRepository()

    result = await run_connection_load(
        target_id="t-1",
        target_url="https://example.org/",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),  # identique au profil
        explicit_confirmation=True,
        precheck_validated=False,
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([_SAMPLE]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=run_repository,
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "id-1",
        now=lambda: NOW,
        profile_id="prof-1",
        profile_repository=profile_repository,
    )

    assert isinstance(result, Ok)
    assert result.value.profile_customized is False


async def test_profile_customized_false_without_profile():
    run_repository = FakeRunRepository()

    result = await run_connection_load(
        target_id="t-1",
        target_url="https://example.org/",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([_SAMPLE]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=run_repository,
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "id-1",
        now=lambda: NOW,
        profile_id=None,
    )

    assert isinstance(result, Ok)
    assert result.value.profile_customized is False


async def test_profile_customized_false_when_profile_repository_not_provided():
    """Meme si profile_id est fourni, l'absence de profile_repository (appelant
    qui ne l'a pas sous la main) ne doit jamais faire planter ni affirmer a
    tort "personnalise" — comparaison impossible = False, comme documente."""
    run_repository = FakeRunRepository()

    result = await run_connection_load(
        target_id="t-1",
        target_url="https://example.org/",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.9),
        explicit_confirmation=True,
        precheck_validated=False,
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([_SAMPLE]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=run_repository,
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "id-1",
        now=lambda: NOW,
        profile_id="prof-1",
        profile_repository=None,
    )

    assert isinstance(result, Ok)
    assert result.value.profile_customized is False
