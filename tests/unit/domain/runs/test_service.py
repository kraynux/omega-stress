from datetime import datetime, timezone

from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import LoadResult, LoadRun
from omega_stress.domain.runs.service import finish

STARTED = datetime(2026, 8, 23, 10, 0, tzinfo=timezone.utc)
FINISHED = datetime(2026, 8, 23, 10, 5, tzinfo=timezone.utc)


def _run(**overrides):
    defaults = dict(
        id="run-1",
        profile_id="profile-1",
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
    )
    defaults.update(overrides)
    return LoadRun(**defaults)


def _result():
    return LoadResult(
        verdict=RunVerdict.SUCCESS,
        requested_rate_per_minute=250,
        observed_rate_per_minute=248.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        total_requests=1250,
    )


def test_finish_sets_finished_at_and_result():
    result = finish(_run(), result=_result(), now=FINISHED)

    assert isinstance(result, Ok)
    finished_run = result.value
    assert finished_run.finished_at == FINISHED
    assert finished_run.result is not None
    assert finished_run.result.verdict is RunVerdict.SUCCESS


def test_finish_rejects_already_finished_run():
    already_finished = _run(finished_at=FINISHED, result=_result())

    result = finish(already_finished, result=_result(), now=FINISHED)

    assert isinstance(result, Err)
