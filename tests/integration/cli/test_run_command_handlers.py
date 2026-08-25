import argparse
import sqlite3
from datetime import datetime, timezone

from omega_stress.app.dependency_container import DependencyContainer
from omega_stress.core.capability_registry import CapabilityRegistry
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from omega_stress.domain.terminal.models import TerminalSignals
from omega_stress.infrastructure.logging.audit_logger import AuditLogger
from omega_stress.interfaces.cli.commands import run_command
from tests.fixtures.fakes import (
    FakeExportRepository,
    FakeLoadRunner,
    FakeProfileRepository,
    FakeRunRepository,
    FakeSettingsStore,
    FakeSystemProbe,
    FakeTargetRepository,
    FakeTerminalDetector,
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


def _build_container(tmp_path, *, samples=None) -> DependencyContainer:
    return DependencyContainer(
        connection=sqlite3.connect(":memory:"),
        profile_repository=FakeProfileRepository(),
        target_repository=FakeTargetRepository(),
        run_repository=FakeRunRepository(),
        export_repository=FakeExportRepository(),
        settings_store=FakeSettingsStore(),
        terminal_detector=FakeTerminalDetector(
            TerminalSignals(family="xterm", columns=80, rows=24)
        ),
        system_probe=FakeSystemProbe(),
        load_runner=FakeLoadRunner(samples or [_sample()]),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
        capability_registry=CapabilityRegistry(),
        exporters={},
    )


def _request_args(**overrides) -> argparse.Namespace:
    defaults = dict(
        target_id="t-1",
        target_url="https://example.org/",
        level="bas",
        duration_minutes=1,
        max_error_rate=0.5,
        max_p95_latency_ms=None,
        profile_id=None,
        confirm=True,
        precheck_validated=False,
        json=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


async def test_handle_request_launches_and_persists(tmp_path):
    container = _build_container(tmp_path)

    result = await run_command._handle_request(_request_args(), container)

    assert isinstance(result, Ok)
    assert "request" in result.value
    assert len(container.run_repository.list_history()) == 1


async def test_handle_request_denied_without_confirmation(tmp_path):
    container = _build_container(tmp_path)

    result = await run_command._handle_request(_request_args(confirm=False), container)

    assert isinstance(result, Err)


async def test_handle_precheck_launches(tmp_path):
    container = _build_container(tmp_path)
    args = argparse.Namespace(
        target_id="t-1", target_url="https://example.org/", confirm=True, json=True
    )

    result = await run_command._handle_precheck(args, container)

    assert isinstance(result, Ok)
    assert '"family": "request"' in result.value


async def test_handle_replay_reruns_against_original_target(tmp_path):
    container = _build_container(tmp_path)
    from omega_stress.core.enums import IntensityLevel, TestFamily
    from omega_stress.domain.load.models import Duration, Thresholds
    from omega_stress.domain.profiles.models import Profile
    from omega_stress.domain.runs.models import LoadRun

    container.profile_repository.save(
        Profile(
            id="profile-1",
            name="Nominal",
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
    )
    target = Target(
        id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW
    )
    container.target_repository.save_pinned(
        PinnedTarget(target=target, pinned_at=NOW, authorized_at=NOW)
    )
    container.run_repository.save(
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
    args = argparse.Namespace(run_id="run-1", confirm=True, precheck_validated=False, json=True)

    result = await run_command._handle_replay(args, container)

    assert isinstance(result, Ok)
    assert '"target_id": "t-1"' in result.value
