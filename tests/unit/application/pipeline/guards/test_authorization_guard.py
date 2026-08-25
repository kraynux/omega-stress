from datetime import datetime, timezone

from omega_stress.application.pipeline.guards.authorization_guard import check_authorization
from omega_stress.core.results import Err, Ok
from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from tests.fixtures.fakes import FakeTargetRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def test_authorized_when_target_is_pinned():
    repo = FakeTargetRepository()
    target = Target(
        id="t-1", address=TargetAddress(scheme="https", host="example.org"), created_at=NOW
    )
    repo.save_pinned(PinnedTarget(target=target, pinned_at=NOW, authorized_at=NOW))

    result = check_authorization("t-1", target_repository=repo, explicit_confirmation=False)

    assert isinstance(result, Ok)


def test_authorized_with_explicit_confirmation_for_unpinned_target():
    repo = FakeTargetRepository()

    result = check_authorization("t-1", target_repository=repo, explicit_confirmation=True)

    assert isinstance(result, Ok)


def test_denied_without_pin_or_confirmation():
    repo = FakeTargetRepository()

    result = check_authorization("t-1", target_repository=repo, explicit_confirmation=False)

    assert isinstance(result, Err)
