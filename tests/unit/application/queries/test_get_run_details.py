from datetime import datetime, timezone

from omega_stress.application.queries.get_run_details import get_run_details
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.runs.models import LoadRun
from tests.fixtures.fakes import FakeRunRepository, FakeTargetRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def test_returns_none_for_unknown_run():
    repo = FakeRunRepository()

    assert (
        get_run_details(
            "does-not-exist", run_repository=repo, target_repository=FakeTargetRepository()
        )
        is None
    )


def test_returns_dto_for_known_run():
    repo = FakeRunRepository()
    repo.save(
        LoadRun(
            id="run-1",
            profile_id=None,
            target_id="t-1",
            family=TestFamily.REQUEST,
            level=IntensityLevel.BAS,
            started_at=NOW,
        )
    )

    dto = get_run_details(
        "run-1", run_repository=repo, target_repository=FakeTargetRepository()
    )

    assert dto is not None
    assert dto.id == "run-1"
    assert dto.target_address == "t-1"
