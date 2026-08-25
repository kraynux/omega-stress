from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.interfaces.tui.presenters.profile_presenter import (
    sorted_for_display,
    status_label,
)


def _profile(name: str, *, favorite: bool = False, frozen: bool = True) -> ProfileDTO:
    return ProfileDTO(
        id=name,
        name=name,
        description="",
        default_target_id="target-1",
        family="request",
        level="moyen",
        duration_minutes=5,
        max_error_rate=0.05,
        max_p95_latency_ms=None,
        tags=(),
        extended_duration_authorized=False,
        frozen=frozen,
        favorite=favorite,
        archived=False,
        created_at="2026-08-24T09:00:00",
        frozen_at="2026-08-24T09:00:00" if frozen else None,
    )


def test_favorites_come_before_non_favorites():
    profiles = (_profile("Zulu"), _profile("Alpha", favorite=True))

    ordered = sorted_for_display(profiles)

    assert [p.name for p in ordered] == ["Alpha", "Zulu"]


def test_same_favorite_status_sorts_alphabetically():
    profiles = (_profile("Bravo"), _profile("Alpha"))

    ordered = sorted_for_display(profiles)

    assert [p.name for p in ordered] == ["Alpha", "Bravo"]


def test_status_label_reflects_frozen_flag():
    assert status_label(_profile("A", frozen=True)) == "Fige"
    assert status_label(_profile("A", frozen=False)) == "Modifiable"
