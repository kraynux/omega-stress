from datetime import datetime, timezone

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.infrastructure.storage.sqlite.profile_repository import (
    SqliteProfileRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _profile(**overrides) -> Profile:
    defaults = dict(
        id="profile-1",
        name="Charge nominale",
        description="Un profil de test",
        default_target_id="target-1",
        family=TestFamily.RAMP,
        level=IntensityLevel.HAUT,
        duration=Duration(minutes=3),
        thresholds=Thresholds(max_error_rate=0.1, max_p95_latency_ms=500.0),
        tags=("web", "prod"),
        extended_duration_authorized=True,
        frozen=True,
        frozen_at=NOW,
        favorite=True,
        archived=False,
        created_at=NOW,
    )
    defaults.update(overrides)
    return Profile(**defaults)


def test_save_and_get_roundtrip_preserves_all_fields(sqlite_connection):
    repo = SqliteProfileRepository(sqlite_connection)
    original = _profile()

    repo.save(original)
    fetched = repo.get("profile-1")

    assert fetched == original


def test_get_unknown_profile_returns_none(sqlite_connection):
    repo = SqliteProfileRepository(sqlite_connection)

    assert repo.get("does-not-exist") is None


def test_save_is_upsert(sqlite_connection):
    repo = SqliteProfileRepository(sqlite_connection)
    repo.save(_profile(name="Version 1"))
    repo.save(_profile(name="Version 2"))

    assert repo.get("profile-1").name == "Version 2"
    assert len(repo.list_all()) == 1


def test_list_all_returns_every_profile(sqlite_connection):
    repo = SqliteProfileRepository(sqlite_connection)
    repo.save(_profile(id="p-1"))
    repo.save(_profile(id="p-2"))

    assert {p.id for p in repo.list_all()} == {"p-1", "p-2"}


def test_delete_removes_profile(sqlite_connection):
    repo = SqliteProfileRepository(sqlite_connection)
    repo.save(_profile())

    repo.delete("profile-1")

    assert repo.get("profile-1") is None


def test_optional_fields_roundtrip_as_none(sqlite_connection):
    repo = SqliteProfileRepository(sqlite_connection)
    profile = _profile(
        thresholds=Thresholds(max_error_rate=0.1), frozen=False, frozen_at=None
    )

    repo.save(profile)
    fetched = repo.get("profile-1")

    assert fetched.thresholds.max_p95_latency_ms is None
    assert fetched.frozen_at is None
