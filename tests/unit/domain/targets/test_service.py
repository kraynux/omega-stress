from datetime import datetime, timezone

from omega_stress.core.results import Err, Ok
from omega_stress.domain.errors import UnauthorizedTargetError
from omega_stress.domain.targets.models import Target, TargetAddress
from omega_stress.domain.targets.service import pin

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _target():
    return Target(
        id="target-1",
        address=TargetAddress(scheme="https", host="example.org"),
        created_at=NOW,
    )


def test_pin_requires_authorization_confirmation():
    result = pin(_target(), authorization_confirmed=False, now=NOW)

    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedTargetError)


def test_pin_succeeds_when_confirmed():
    result = pin(_target(), authorization_confirmed=True, now=NOW)

    assert isinstance(result, Ok)
    pinned = result.value
    assert pinned.target == _target()
    assert pinned.pinned_at == NOW
    assert pinned.authorized_at == NOW
