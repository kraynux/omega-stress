from datetime import datetime, timezone

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Duration, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.profiles.validation import validate_profile

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _profile(**overrides):
    defaults = dict(
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
    defaults.update(overrides)
    return Profile(**defaults)


def test_valid_profile_passes():
    assert isinstance(validate_profile(_profile()), Ok)


def test_blank_name_is_rejected():
    result = validate_profile(_profile(name="   "))
    assert isinstance(result, Err)


def test_extended_duration_requires_explicit_authorization():
    result = validate_profile(
        _profile(
            level=IntensityLevel.PUISSANT,
            duration=Duration(minutes=5),
            extended_duration_authorized=False,
        )
    )
    assert isinstance(result, Err)


def test_extended_duration_allowed_when_authorized():
    result = validate_profile(
        _profile(
            level=IntensityLevel.PUISSANT,
            duration=Duration(minutes=5),
            extended_duration_authorized=True,
        )
    )
    assert isinstance(result, Ok)
