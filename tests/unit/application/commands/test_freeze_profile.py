from datetime import datetime, timezone

from omega_stress.application.commands.freeze_profile import freeze_profile
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from tests.fixtures.fakes import FakeProfileRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)
LATER = datetime(2026, 8, 25, tzinfo=timezone.utc)


def _profile() -> Profile:
    return Profile(
        id="profile-1",
        name="Charge nominale",
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.1),
        created_at=NOW,
    )


def test_freezes_and_persists_existing_profile():
    repo = FakeProfileRepository()
    repo.save(_profile())

    result = freeze_profile("profile-1", profile_repository=repo, now=LATER)

    assert isinstance(result, Ok)
    assert result.value.frozen is True
    assert repo.get("profile-1").frozen is True  # type: ignore[union-attr]


def test_returns_error_for_unknown_profile():
    repo = FakeProfileRepository()

    result = freeze_profile("does-not-exist", profile_repository=repo, now=LATER)

    assert isinstance(result, Err)
