from datetime import datetime, timezone

from omega_stress.application.commands.pin_target import pin_target
from omega_stress.core.results import Err, Ok
from tests.fixtures.fakes import FakeTargetRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _id_factory():
    return "target-1"


def test_pins_target_when_authorized():
    repo = FakeTargetRepository()

    result = pin_target(
        target_repository=repo,
        id_factory=_id_factory,
        now=NOW,
        raw_address="example.org",
        authorization_confirmed=True,
    )

    assert isinstance(result, Ok)
    assert repo.get_pinned("target-1") is not None


def test_rejects_when_not_authorized():
    repo = FakeTargetRepository()

    result = pin_target(
        target_repository=repo,
        id_factory=_id_factory,
        now=NOW,
        raw_address="example.org",
        authorization_confirmed=False,
    )

    assert isinstance(result, Err)
    assert repo.get_pinned("target-1") is None


def test_rejects_invalid_address_before_checking_authorization():
    repo = FakeTargetRepository()

    result = pin_target(
        target_repository=repo,
        id_factory=_id_factory,
        now=NOW,
        raw_address="   ",
        authorization_confirmed=True,
    )

    assert isinstance(result, Err)
    assert repo.get_pinned("target-1") is None
