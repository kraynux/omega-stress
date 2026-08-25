from datetime import datetime, timezone

from omega_stress.application.queries.list_history import list_history
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.runs.models import LoadRun
from tests.fixtures.fakes import FakeRunRepository, FakeTargetRepository


def _run(
    run_id: str,
    *,
    target_id: str = "t-1",
    profile_id: str | None = "p-1",
    started_at=None,
) -> LoadRun:
    return LoadRun(
        id=run_id,
        profile_id=profile_id,
        target_id=target_id,
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=started_at or datetime(2026, 8, 24, tzinfo=timezone.utc),
    )


def test_filters_by_target_id():
    repo = FakeRunRepository()
    repo.save(_run("r-1", target_id="t-1"))
    repo.save(_run("r-2", target_id="t-2"))

    result = list_history(
        run_repository=repo, target_repository=FakeTargetRepository(), target_id="t-1"
    )

    assert [dto.id for dto in result] == ["r-1"]


def test_filters_by_profile_id():
    repo = FakeRunRepository()
    repo.save(_run("r-1", profile_id="p-1"))
    repo.save(_run("r-2", profile_id="p-2"))

    result = list_history(
        run_repository=repo, target_repository=FakeTargetRepository(), profile_id="p-2"
    )

    assert [dto.id for dto in result] == ["r-2"]


def test_respects_limit():
    repo = FakeRunRepository()
    for i in range(3):
        repo.save(_run(f"r-{i}"))

    result = list_history(run_repository=repo, target_repository=FakeTargetRepository(), limit=2)

    assert len(result) == 2
