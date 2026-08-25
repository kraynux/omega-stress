from datetime import datetime, timezone

from omega_stress.application.queries.list_profiles import list_profiles
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from tests.fixtures.fakes import FakeProfileRepository

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _profile(profile_id: str, *, archived: bool = False) -> Profile:
    return Profile(
        id=profile_id,
        name=f"Profile {profile_id}",
        description="",
        default_target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.1),
        created_at=NOW,
        archived=archived,
    )


def test_excludes_archived_profiles_by_default():
    repo = FakeProfileRepository()
    repo.save(_profile("p-1"))
    repo.save(_profile("p-2", archived=True))

    result = list_profiles(profile_repository=repo)

    assert [dto.id for dto in result] == ["p-1"]


def test_includes_archived_when_requested():
    repo = FakeProfileRepository()
    repo.save(_profile("p-1"))
    repo.save(_profile("p-2", archived=True))

    result = list_profiles(profile_repository=repo, include_archived=True)

    assert {dto.id for dto in result} == {"p-1", "p-2"}
