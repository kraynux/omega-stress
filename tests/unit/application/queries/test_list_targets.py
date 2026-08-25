from datetime import datetime, timezone

from omega_stress.application.queries.list_targets import list_targets
from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from tests.fixtures.fakes import FakeTargetRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _target(target_id: str) -> Target:
    return Target(
        id=target_id,
        address=TargetAddress(scheme="https", host=f"{target_id}.example.org"),
        created_at=NOW,
    )


def test_pinned_targets_come_first_and_recent_duplicates_are_excluded():
    repo = FakeTargetRepository()
    pinned_target = _target("t-pinned")
    repo.save_pinned(PinnedTarget(target=pinned_target, pinned_at=NOW, authorized_at=NOW))
    repo.save_recent(pinned_target)  # meme cible aussi presente en recent
    repo.save_recent(_target("t-recent"))

    result = list_targets(target_repository=repo)

    assert [dto.id for dto in result] == ["t-pinned", "t-recent"]
    assert result[0].pinned is True
    assert result[1].pinned is False


def test_recent_limit_is_respected():
    repo = FakeTargetRepository()
    for i in range(5):
        repo.save_recent(_target(f"t-{i}"))

    result = list_targets(target_repository=repo, recent_limit=2)

    assert len(result) == 2
