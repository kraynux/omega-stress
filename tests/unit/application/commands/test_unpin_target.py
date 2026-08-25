from datetime import datetime, timezone

from omega_stress.application.commands.unpin_target import unpin_target
from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from tests.fixtures.fakes import FakeTargetRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def test_unpin_removes_pinned_target():
    repo = FakeTargetRepository()
    target = Target(
        id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW
    )
    repo.save_pinned(PinnedTarget(target=target, pinned_at=NOW, authorized_at=NOW))

    unpin_target("t-1", target_repository=repo)

    assert repo.get_pinned("t-1") is None


def test_unpin_is_idempotent_for_unknown_target():
    repo = FakeTargetRepository()

    unpin_target("does-not-exist", target_repository=repo)  # ne leve pas
