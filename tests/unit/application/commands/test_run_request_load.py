from datetime import datetime, timezone

from omega_stress.application.commands.run_request_load import run_request_load
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.runs.models import IntervalSample
from tests.fixtures.fakes import (
    FakeLoadRunner,
    FakeRunProgressNotifier,
    FakeRunRepository,
    FakeTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


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


async def _run(**overrides):
    defaults = dict(
        target_id="t-1",
        target_url="https://example.org/",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([_sample()]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=FakeRunRepository(),
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "id-1",
        now=lambda: NOW,
    )
    defaults.update(overrides)
    return await run_request_load(**defaults)


async def test_bas_level_launches_without_precheck():
    result = await _run()

    assert isinstance(result, Ok)
    assert result.value.family == "request"


async def test_successful_launch_persists_the_run():
    run_repository = FakeRunRepository()

    result = await _run(run_repository=run_repository)

    assert isinstance(result, Ok)
    assert run_repository.get(result.value.id) is not None


async def test_denied_without_authorization():
    result = await _run(explicit_confirmation=False)

    assert isinstance(result, Err)


async def test_violent_level_denied_without_precheck():
    result = await _run(level=IntensityLevel.VIOLENT, precheck_validated=False)

    assert isinstance(result, Err)


async def test_violent_level_allowed_with_precheck():
    result = await _run(level=IntensityLevel.VIOLENT, precheck_validated=True)

    assert isinstance(result, Ok)


async def test_disallowed_duration_is_rejected():
    result = await _run(duration_minutes=7)

    assert isinstance(result, Err)


async def test_safety_mode_defaults_to_true_and_is_persisted_on_the_run():
    run_repository = FakeRunRepository()

    result = await _run(run_repository=run_repository)

    assert isinstance(result, Ok)
    saved = run_repository.get(result.value.id)
    assert saved is not None
    assert saved.safety_mode is True


async def test_safety_mode_false_is_transmitted_and_persisted_on_the_run():
    run_repository = FakeRunRepository()

    result = await _run(run_repository=run_repository, safety_mode=False)

    assert isinstance(result, Ok)
    saved = run_repository.get(result.value.id)
    assert saved is not None
    assert saved.safety_mode is False


async def test_successful_launch_persists_the_target_as_recent():
    """Regression : avant le 2026-08-24, une cible en mode manuel n'etait
    jamais persistee, cassant a la fois la liste des cibles recentes et
    replay_run.py (qui a besoin de target_repository.get() plus tard)."""
    target_repository = FakeTargetRepository()

    result = await _run(target_repository=target_repository)

    assert isinstance(result, Ok)
    saved = target_repository.get("t-1")
    assert saved is not None
    assert saved.address.base_url == "https://example.org/"
