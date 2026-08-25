from datetime import datetime, timezone

from omega_stress.domain.targets.models import PinnedTarget, Target, TargetAddress
from omega_stress.infrastructure.storage.sqlite.target_repository import (
    SqliteTargetRepository,
)

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def _target(target_id: str = "t-1") -> Target:
    return Target(
        id=target_id,
        address=TargetAddress(scheme="https", host="example.org", port=8443, path="/api"),
        created_at=NOW,
        tags=("prod",),
        notes="cible principale",
        last_used_at=NOW,
    )


def test_save_recent_and_list_recent_roundtrip(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    repo.save_recent(_target())

    recent = repo.list_recent()

    assert len(recent) == 1
    assert recent[0] == _target()


def test_save_pinned_and_get_pinned_roundtrip(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    pinned = PinnedTarget(target=_target(), pinned_at=NOW, authorized_at=NOW)

    repo.save_pinned(pinned)

    assert repo.get_pinned("t-1") == pinned


def test_get_resolves_pinned_target_even_without_recent_entry(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    repo.save_pinned(PinnedTarget(target=_target(), pinned_at=NOW, authorized_at=NOW))

    assert repo.get("t-1") == _target()


def test_get_resolves_recent_only_target(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    repo.save_recent(_target())

    assert repo.get("t-1") == _target()


def test_get_unknown_target_returns_none(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)

    assert repo.get("does-not-exist") is None


def test_unpin_removes_from_pinned_but_not_recent(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    repo.save_recent(_target())
    repo.save_pinned(PinnedTarget(target=_target(), pinned_at=NOW, authorized_at=NOW))

    repo.unpin("t-1")

    assert repo.get_pinned("t-1") is None
    assert repo.get("t-1") == _target()  # toujours resolvable via la table targets


def test_list_pinned_returns_every_pinned_target(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    repo.save_pinned(PinnedTarget(target=_target("t-1"), pinned_at=NOW, authorized_at=NOW))
    repo.save_pinned(PinnedTarget(target=_target("t-2"), pinned_at=NOW, authorized_at=NOW))

    assert {p.target.id for p in repo.list_pinned()} == {"t-1", "t-2"}


def test_list_recent_respects_limit(sqlite_connection):
    repo = SqliteTargetRepository(sqlite_connection)
    for i in range(5):
        repo.save_recent(_target(f"t-{i}"))

    assert len(repo.list_recent(limit=2)) == 2
