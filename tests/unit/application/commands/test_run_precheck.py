from datetime import datetime, timezone

from omega_stress.application.commands.run_precheck import run_precheck
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import IntervalSample
from tests.fixtures.fakes import (
    FakeLoadRunner,
    FakeRunProgressNotifier,
    FakeRunRepository,
    FakeTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _sample() -> IntervalSample:
    return IntervalSample(
        at_second=1.0,
        observed_rate_per_minute=50.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=5,
    )


async def _run(explicit_confirmation: bool):
    target_repository = FakeTargetRepository()
    notifier = FakeRunProgressNotifier()
    audit_events: list = []

    return await run_precheck(
        target_id="t-1",
        target_url="https://example.org/",
        target_repository=target_repository,
        load_runner=FakeLoadRunner([_sample()]),
        run_progress_notifier=notifier,
        run_repository=FakeRunRepository(),
        audit_sink=audit_events.append,
        notification_sink=lambda _msg: None,
        id_factory=lambda: "id-1",
        explicit_confirmation=explicit_confirmation,
        now=lambda: NOW,
    )


async def test_precheck_succeeds_with_confirmation():
    result = await _run(explicit_confirmation=True)

    assert isinstance(result, Ok)
    assert result.value.family == "request"
    assert result.value.level == "faible"


async def test_precheck_denied_without_confirmation():
    result = await _run(explicit_confirmation=False)

    assert isinstance(result, Err)


async def test_precheck_persists_the_run():
    run_repository = FakeRunRepository()

    result = await run_precheck(
        target_id="t-1",
        target_url="https://example.org/",
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([_sample()]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=run_repository,
        audit_sink=lambda _e: None,
        notification_sink=lambda _msg: None,
        id_factory=lambda: "id-1",
        explicit_confirmation=True,
        now=lambda: NOW,
    )

    assert isinstance(result, Ok)
    persisted = run_repository.get(result.value.id)
    assert persisted is not None
    assert persisted.is_precheck is True
