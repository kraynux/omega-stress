from types import SimpleNamespace

from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Thresholds
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.infrastructure.logging.audit_logger import AuditLogger
from omega_stress.interfaces.tui.controllers import load_controller
from tests.fixtures.fakes import (
    FakeLoadRunner,
    FakeProfileRepository,
    FakeRunRepository,
    FakeSystemProbe,
    FakeTargetRepository,
)


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


def _container(tmp_path, *, samples=None, capabilities=()):
    return SimpleNamespace(
        target_repository=FakeTargetRepository(),
        profile_repository=FakeProfileRepository(),
        run_repository=FakeRunRepository(),
        load_runner=FakeLoadRunner(samples if samples is not None else [_sample()]),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
        capability_registry=CapabilityRegistry(),
        system_probe=FakeSystemProbe(capabilities),
    )


class _RecordingProgressNotifier:
    def __init__(self) -> None:
        self.notifications: list[tuple[str, IntervalSample]] = []

    def notify(self, run_id: str, sample: IntervalSample) -> None:
        self.notifications.append((run_id, sample))


class _RecordingNotificationSink:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, message: str) -> None:
        self.messages.append(message)


async def test_launch_precheck_succeeds_with_explicit_confirmation(tmp_path):
    container = _container(tmp_path)

    result = await load_controller.launch_precheck(
        container=container,
        target_id="target-1",
        target_url="https://exemple.org",
        explicit_confirmation=True,
        run_progress_notifier=_RecordingProgressNotifier(),
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Ok)
    assert container.run_repository.get(result.value.id) is not None


async def test_launch_precheck_denied_without_confirmation(tmp_path):
    container = _container(tmp_path)

    result = await load_controller.launch_precheck(
        container=container,
        target_id="target-1",
        target_url="https://exemple.org",
        explicit_confirmation=False,
        run_progress_notifier=_RecordingProgressNotifier(),
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Err)


async def test_launch_request_bas_level_succeeds_and_persists(tmp_path):
    container = _container(tmp_path)
    progress_notifier = _RecordingProgressNotifier()

    result = await load_controller.launch_request(
        container=container,
        target_id="target-1",
        target_url="https://exemple.org",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        run_progress_notifier=progress_notifier,
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Ok)
    assert container.run_repository.get(result.value.id) is not None
    assert len(progress_notifier.notifications) == 1


async def test_launch_request_violent_level_denied_without_precheck(tmp_path):
    container = _container(tmp_path)

    result = await load_controller.launch_request(
        container=container,
        target_id="target-1",
        target_url="https://exemple.org",
        level=IntensityLevel.VIOLENT,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        run_progress_notifier=_RecordingProgressNotifier(),
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Err)


async def test_launch_connection_succeeds(tmp_path):
    container = _container(tmp_path)

    result = await load_controller.launch_connection(
        container=container,
        target_id="target-1",
        target_url="https://exemple.org",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        run_progress_notifier=_RecordingProgressNotifier(),
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Ok)
    assert result.value.family == "connection"


async def test_launch_ramp_succeeds(tmp_path):
    container = _container(tmp_path)

    result = await load_controller.launch_ramp(
        container=container,
        target_id="target-1",
        target_url="https://exemple.org",
        level=IntensityLevel.BAS,
        duration_minutes=1,
        thresholds=Thresholds(max_error_rate=0.5),
        explicit_confirmation=True,
        precheck_validated=False,
        run_progress_notifier=_RecordingProgressNotifier(),
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Ok)
    assert result.value.family == "ramp"


async def test_launch_replay_unknown_run_returns_err(tmp_path):
    container = _container(tmp_path)

    result = await load_controller.launch_replay(
        "unknown-run",
        container=container,
        explicit_confirmation=True,
        precheck_validated=False,
        run_progress_notifier=_RecordingProgressNotifier(),
        notification_sink=_RecordingNotificationSink(),
    )

    assert isinstance(result, Err)


def test_pin_new_target_requires_authorization_confirmation():
    repository = FakeTargetRepository()

    result = load_controller.pin_new_target(
        target_repository=repository,
        raw_address="https://exemple.org",
        authorization_confirmed=False,
    )

    assert isinstance(result, Err)


def test_pin_new_target_succeeds_and_is_listed():
    repository = FakeTargetRepository()

    result = load_controller.pin_new_target(
        target_repository=repository,
        raw_address="https://exemple.org",
        authorization_confirmed=True,
    )

    assert isinstance(result, Ok)
    targets = load_controller.load_targets(target_repository=repository)
    assert any(t.id == result.value.id and t.pinned for t in targets)


def test_unpin_existing_target_removes_it_from_pinned_list():
    repository = FakeTargetRepository()
    pinned = load_controller.pin_new_target(
        target_repository=repository,
        raw_address="https://exemple.org",
        authorization_confirmed=True,
    )
    assert isinstance(pinned, Ok)

    load_controller.unpin_existing_target(pinned.value.id, target_repository=repository)

    targets = load_controller.load_targets(target_repository=repository)
    assert not any(t.id == pinned.value.id and t.pinned for t in targets)
