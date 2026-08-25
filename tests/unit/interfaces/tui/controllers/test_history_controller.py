from datetime import datetime, timezone

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.runs.models import LoadRun
from omega_stress.interfaces.tui.controllers.history_controller import (
    load_history,
    run_details,
)
from tests.fixtures.fakes import FakeRunRepository, FakeTargetRepository


def _run(run_id: str, started_at: datetime) -> LoadRun:
    return LoadRun(
        id=run_id,
        profile_id=None,
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=started_at,
    )


def test_load_history_orders_most_recent_first():
    repository = FakeRunRepository()
    repository.save(_run("older", datetime(2026, 8, 20, tzinfo=timezone.utc)))
    repository.save(_run("newer", datetime(2026, 8, 24, tzinfo=timezone.utc)))

    runs = load_history(run_repository=repository, target_repository=FakeTargetRepository())

    assert [r.id for r in runs] == ["newer", "older"]


def test_run_details_returns_none_for_unknown_run():
    repository = FakeRunRepository()

    assert (
        run_details(
            "unknown", run_repository=repository, target_repository=FakeTargetRepository()
        )
        is None
    )


def test_run_details_returns_dto_for_known_run():
    repository = FakeRunRepository()
    repository.save(_run("run-1", datetime(2026, 8, 24, tzinfo=timezone.utc)))

    details = run_details(
        "run-1", run_repository=repository, target_repository=FakeTargetRepository()
    )

    assert details is not None
    assert details.id == "run-1"
