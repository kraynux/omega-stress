from datetime import datetime, timezone

from omega_stress.application.commands.create_profile import create_profile
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from tests.fixtures.fakes import FakeProfileRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _id_factory():
    return "profile-1"


def test_creates_and_persists_a_valid_profile():
    repo = FakeProfileRepository()

    result = create_profile(
        profile_repository=repo,
        id_factory=_id_factory,
        now=NOW,
        name="Charge nominale",
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration_minutes=1,
        max_error_rate=0.1,
    )

    assert isinstance(result, Ok)
    assert repo.get("profile-1") is not None
    assert result.value.name == "Charge nominale"


def test_rejects_disallowed_duration_without_persisting():
    repo = FakeProfileRepository()

    result = create_profile(
        profile_repository=repo,
        id_factory=_id_factory,
        now=NOW,
        name="Trop long",
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.HAUT,
        duration_minutes=5,
        max_error_rate=0.1,
    )

    assert isinstance(result, Err)
    assert repo.get("profile-1") is None


def test_rejects_blank_name_without_persisting():
    repo = FakeProfileRepository()

    result = create_profile(
        profile_repository=repo,
        id_factory=_id_factory,
        now=NOW,
        name="   ",
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration_minutes=1,
        max_error_rate=0.1,
    )

    assert isinstance(result, Err)
    assert repo.get("profile-1") is None
