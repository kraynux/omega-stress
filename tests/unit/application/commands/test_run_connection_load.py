from datetime import datetime, timezone

from omega_stress.application.commands.run_connection_load import run_connection_load
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Ok
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.runs.models import IntervalSample
from tests.fixtures.fakes import (
    FakeLoadRunner,
    FakeRunProgressNotifier,
    FakeRunRepository,
    FakeTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


async def test_connection_load_launches_and_reports_no_requested_rate():
    sample = IntervalSample(
        at_second=1.0,
        observed_rate_per_minute=0.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=0,
    )

    result = await run_connection_load(
        target_id="t-1",
        target_url="https://example.org/",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        target_repository=FakeTargetRepository(),
        load_runner=FakeLoadRunner([sample]),
        run_progress_notifier=FakeRunProgressNotifier(),
        run_repository=FakeRunRepository(),
        audit_sink=lambda _e: None,
        notification_sink=lambda _m: None,
        id_factory=lambda: "id-1",
        now=lambda: NOW,
    )

    assert isinstance(result, Ok)
    assert result.value.family == "connection"
