from datetime import datetime, timezone

from omega_stress.application.commands.run_calibration import run_calibration
from omega_stress.core.results import Err, Ok
from omega_stress.domain.calibration.models import (
    CalibrationFingerprint,
    CalibrationPreconditionsSnapshot,
    StageMeasurement,
)

NOW = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)


def _fingerprint() -> CalibrationFingerprint:
    return CalibrationFingerprint(
        schema_version=1,
        engine_version="1.0.0",
        python_version="3.14.0",
        os_name="Linux",
        architecture="x86_64",
        logical_cpu_count=4,
        total_ram_mb=8192.0,
        open_files_soft_limit=1024,
        workers_mode="asyncio-single-process",
        scenario_id="payload-4k",
    )


def _idle_snapshot() -> CalibrationPreconditionsSnapshot:
    return CalibrationPreconditionsSnapshot(
        cpu_global_percent=5.0,
        memory_available_percent=80.0,
        swap_active_or_growing=False,
        load_average_1min=0.5,
        logical_cpu_count=4,
    )


class _FakePreconditionsProbe:
    def __init__(self, snapshot: CalibrationPreconditionsSnapshot) -> None:
        self._snapshot = snapshot

    async def read(self) -> CalibrationPreconditionsSnapshot:
        return self._snapshot


class _FakeServer:
    def __enter__(self) -> "_FakeServer":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    @property
    def base_url(self) -> str:
        return "http://127.0.0.1:9"


class _FakeStageRunner:
    def __init__(self, measurement_overrides: dict[str, StageMeasurement] | None = None) -> None:
        self._overrides = measurement_overrides or {}
        self.stage_ids_run: list[str] = []

    async def __aenter__(self) -> "_FakeStageRunner":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        return None

    async def run_stage(
        self, stage, *, base_url: str, stage_progress_notifier
    ) -> StageMeasurement:  # noqa: ANN001
        self.stage_ids_run.append(stage.id)
        stage_progress_notifier.notify(stage.id, stage.window_seconds, stage.window_seconds)
        if stage.id in self._overrides:
            return self._overrides[stage.id]
        return StageMeasurement(
            rps_achieved=float(stage.rps_target),
            error_rate=0.0,
            system_samples=(),
            consecutive_timeouts=0,
        )


class _FakeStageProgressNotifier:
    def __init__(self, calls: list[tuple[str, int, int]]) -> None:
        self._calls = calls

    def notify(self, stage_id: str, elapsed_seconds: int, window_seconds: int) -> None:
        self._calls.append((stage_id, elapsed_seconds, window_seconds))


class _FakeRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, result) -> None:  # noqa: ANN001
        self.saved.append(result)

    def load(self, fingerprint_hash: str):  # noqa: ANN001
        return None


async def _run(
    *,
    snapshot=None,
    measurement_overrides=None,
    another_active=False,
):
    stage_runner = _FakeStageRunner(measurement_overrides)
    repository = _FakeRepository()
    notifications: list[str] = []
    stage_progress: list[tuple[str, int, int]] = []

    outcome = await run_calibration(
        compute_fingerprint=_fingerprint,
        preconditions_probe=_FakePreconditionsProbe(snapshot or _idle_snapshot()),
        server_factory=_FakeServer,
        stage_runner_factory=lambda: stage_runner,
        calibration_repository=repository,
        stage_progress_notifier=_FakeStageProgressNotifier(stage_progress),
        now=lambda: NOW,
        notification_sink=notifications.append,
        another_calibration_or_run_active=another_active,
    )
    return outcome, stage_runner, repository, notifications, stage_progress


async def test_denied_by_preconditions_never_starts_server_or_saves():
    bad_snapshot = CalibrationPreconditionsSnapshot(
        cpu_global_percent=90.0,
        memory_available_percent=80.0,
        swap_active_or_growing=False,
        load_average_1min=0.5,
        logical_cpu_count=4,
    )

    outcome, stage_runner, repository, _, _ = await _run(snapshot=bad_snapshot)

    assert isinstance(outcome, Err)
    assert stage_runner.stage_ids_run == []
    assert repository.saved == []


async def test_another_active_calibration_is_refused():
    outcome, *_ = await _run(another_active=True)

    assert isinstance(outcome, Err)


async def test_full_progression_runs_all_seven_stages_when_all_healthy():
    outcome, stage_runner, repository, notifications, stage_progress = await _run()

    assert isinstance(outcome, Ok)
    assert [s.stage_id for s in outcome.value.stages] == stage_runner.stage_ids_run
    assert len(outcome.value.stages) == 7
    assert outcome.value.envelope is not None
    assert outcome.value.envelope.last_healthy_stage_id == "calib_6"
    assert outcome.value.envelope.confidence == "elevee"
    assert len(repository.saved) == 1
    assert repository.saved[0] == outcome.value
    assert len(notifications) == 7
    # stage_progress_notifier (2026-09-02, bug reel corrige : "le
    # calibrage semble geler") : transmis a chaque appel de run_stage(),
    # une notification par palier ici (le fake ne simule qu'un seul appel
    # a notify() par palier, voir _FakeStageRunner.run_stage()).
    assert [stage_id for stage_id, _, _ in stage_progress] == stage_runner.stage_ids_run


async def test_conditional_stages_are_skipped_after_an_unhealthy_stage():
    # calib_4 cible 3000 RPS ; 1500 (50%) est sous le seuil de sante mais
    # ne declenche pas d'arret a lui seul (un seul palier isole).
    overrides = {
        "calib_4": StageMeasurement(
            rps_achieved=1500.0, error_rate=0.0, system_samples=(), consecutive_timeouts=0
        )
    }

    outcome, stage_runner, _, _, _ = await _run(measurement_overrides=overrides)

    assert isinstance(outcome, Ok)
    assert stage_runner.stage_ids_run == [
        "idle_baseline",
        "calib_1",
        "calib_2",
        "calib_3",
        "calib_4",
    ]
    assert "calib_5" not in stage_runner.stage_ids_run
    assert "calib_6" not in stage_runner.stage_ids_run
    assert outcome.value.envelope is not None
    assert outcome.value.envelope.last_healthy_stage_id == "calib_3"


async def test_stage_result_stop_reason_halts_progression_immediately():
    overrides = {
        "calib_2": StageMeasurement(
            rps_achieved=500.0, error_rate=0.02, system_samples=(), consecutive_timeouts=0
        )
    }

    outcome, stage_runner, _, _, _ = await _run(measurement_overrides=overrides)

    assert isinstance(outcome, Ok)
    assert stage_runner.stage_ids_run == ["idle_baseline", "calib_1", "calib_2"]
    assert outcome.value.overall_stop_reason == "error_rate_high"
