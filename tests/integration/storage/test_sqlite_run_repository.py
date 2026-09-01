from datetime import datetime, timezone

from omega_stress.core.enums import DurationPresetId, IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.runs.models import (
    ErrorBreakdown,
    IntervalSample,
    LoadResult,
    LoadRun,
    RunEvent,
    SystemSnapshot,
)
from omega_stress.infrastructure.storage.sqlite.run_repository import SqliteRunRepository

STARTED = datetime(2026, 8, 24, 10, 0, tzinfo=timezone.utc)
FINISHED = datetime(2026, 8, 24, 10, 5, tzinfo=timezone.utc)


def _ongoing_run(run_id: str = "run-1", **overrides) -> LoadRun:
    defaults = dict(
        id=run_id,
        profile_id="profile-1",
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
    )
    defaults.update(overrides)
    return LoadRun(**defaults)


def _finished_run(run_id: str = "run-1", **overrides) -> LoadRun:
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
    return _ongoing_run(run_id, finished_at=FINISHED, result=result, **overrides)


def test_ongoing_run_roundtrips_without_result(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run())

    fetched = repo.get("run-1")

    assert fetched == _ongoing_run()
    assert fetched.result is None


def test_finished_run_roundtrips_with_result(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    original = _finished_run()

    repo.save(original)
    fetched = repo.get("run-1")

    assert fetched == original


def test_get_unknown_run_returns_none(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)

    assert repo.get("does-not-exist") is None


def test_list_history_filters_by_target_and_profile(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_finished_run("r-1", target_id="t-1", profile_id="p-1"))
    repo.save(_finished_run("r-2", target_id="t-2", profile_id="p-1"))
    repo.save(_finished_run("r-3", target_id="t-1", profile_id="p-2"))

    by_target = repo.list_history(target_id="t-1")
    by_profile = repo.list_history(profile_id="p-1")

    assert {r.id for r in by_target} == {"r-1", "r-3"}
    assert {r.id for r in by_profile} == {"r-1", "r-2"}


def test_list_history_respects_limit(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    for i in range(5):
        repo.save(_finished_run(f"r-{i}"))

    assert len(repo.list_history(limit=2)) == 2


def test_events_and_samples_roundtrip(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
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
            RunEvent(occurred_at=FINISHED, kind="runner_failure", message="cible injoignable"),
        ),
        samples=(
            IntervalSample(
                at_second=0.0,
                observed_rate_per_minute=100.0,
                p50_latency_ms=10.0,
                p95_latency_ms=20.0,
                p99_latency_ms=30.0,
                error_count=0,
                request_count=5,
            ),
            IntervalSample(
                at_second=1.0,
                observed_rate_per_minute=110.0,
                p50_latency_ms=11.0,
                p95_latency_ms=21.0,
                p99_latency_ms=31.0,
                error_count=1,
                request_count=6,
            ),
        ),
    )
    original = _ongoing_run(finished_at=FINISHED, result=result)

    repo.save(original)
    fetched = repo.get("run-1")

    assert fetched == original
    assert fetched.result.events == result.events
    assert fetched.result.samples == result.samples


def test_error_breakdown_and_system_snapshot_roundtrip(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    result = LoadResult(
        verdict=RunVerdict.DEGRADED,
        requested_rate_per_minute=250,
        observed_rate_per_minute=200.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=3,
        total_requests=250,
        errors=ErrorBreakdown(timeout=1, connection=1, http_5xx=1),
        peak_cpu_percent_generator=87.5,
        peak_memory_rss_mb=512.0,
        samples=(
            IntervalSample(
                at_second=0.0,
                observed_rate_per_minute=200.0,
                p50_latency_ms=10.0,
                p95_latency_ms=20.0,
                p99_latency_ms=30.0,
                error_count=1,
                request_count=5,
                requested_rate_per_minute=250.0,
                active_connections=10,
                errors=ErrorBreakdown(timeout=1),
                system=SystemSnapshot(
                    cpu_percent_generator=45.0,
                    cpu_percent_global=30.0,
                    memory_available_percent=60.0,
                    memory_rss_mb=256.0,
                    swap_used_mb=0.0,
                    open_files=42,
                    open_files_soft_limit=1024,
                    logical_cpu_count=4,
                ),
            ),
            IntervalSample(
                at_second=1.0,
                observed_rate_per_minute=200.0,
                p50_latency_ms=10.0,
                p95_latency_ms=20.0,
                p99_latency_ms=30.0,
                error_count=0,
                request_count=5,
                system=None,  # mesure absente sur cet intervalle : doit rester None au retour
            ),
        ),
    )
    original = _ongoing_run(finished_at=FINISHED, result=result)

    repo.save(original)
    fetched = repo.get("run-1")

    assert fetched == original
    assert fetched.result.errors == ErrorBreakdown(timeout=1, connection=1, http_5xx=1)
    assert fetched.result.peak_cpu_percent_generator == 87.5
    assert fetched.result.samples[0].system == result.samples[0].system
    assert fetched.result.samples[0].system.open_files_soft_limit == 1024
    assert fetched.result.samples[0].system.logical_cpu_count == 4
    assert fetched.result.samples[1].system is None


def test_precheck_flag_roundtrips(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run(profile_id=None, is_precheck=True))

    fetched = repo.get("run-1")

    assert fetched.is_precheck is True
    assert fetched.profile_id is None


def test_duration_preset_id_roundtrips(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run(duration_preset_id=DurationPresetId.D3))

    fetched = repo.get("run-1")

    assert fetched.duration_preset_id is DurationPresetId.D3


def test_duration_preset_id_defaults_to_none_in_manual_mode(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run())

    fetched = repo.get("run-1")

    assert fetched.duration_preset_id is None


def test_safety_mode_true_roundtrips(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run(safety_mode=True))

    fetched = repo.get("run-1")

    assert fetched.safety_mode is True


def test_safety_mode_false_roundtrips(sqlite_connection):
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run(safety_mode=False))

    fetched = repo.get("run-1")

    assert fetched.safety_mode is False


def test_safety_mode_null_row_is_read_as_true(sqlite_connection):
    # Un run ecrit avant l'existence de cette colonne additive lit NULL —
    # doit se relire comme True (garde-fous toujours actifs a l'epoque),
    # jamais False (voir infrastructure/storage/sqlite/run_repository.py,
    # INFO DEV).
    repo = SqliteRunRepository(sqlite_connection)
    repo.save(_ongoing_run())
    sqlite_connection.execute("UPDATE runs SET safety_mode = NULL WHERE id = ?", ("run-1",))
    sqlite_connection.commit()

    fetched = repo.get("run-1")

    assert fetched.safety_mode is True
