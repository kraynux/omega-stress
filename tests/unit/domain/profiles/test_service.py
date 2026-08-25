from datetime import datetime, timezone

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.profiles.service import duplicate, freeze, to_load_plan

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)
LATER = datetime(2026, 8, 24, tzinfo=timezone.utc)


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


def test_freeze_marks_profile_frozen():
    result = freeze(_profile(), now=LATER)

    assert isinstance(result, Ok)
    frozen = result.value
    assert frozen.frozen is True
    assert frozen.frozen_at == LATER


def test_freeze_is_idempotent_for_already_frozen_profile():
    already_frozen = _profile(frozen=True, frozen_at=NOW)

    result = freeze(already_frozen, now=LATER)

    assert isinstance(result, Ok)
    assert result.value.frozen_at == NOW  # inchange, pas re-fige


def test_freeze_rejects_invalid_profile():
    invalid = _profile(name="   ")

    result = freeze(invalid, now=LATER)

    assert isinstance(result, Err)


def test_duplicate_produces_independent_unfrozen_copy():
    original = freeze(_profile(), now=NOW).value

    copy = duplicate(original, new_id="profile-2", now=LATER)

    assert copy.id == "profile-2"
    assert copy.name == "Charge nominale (copie)"
    assert copy.frozen is False
    assert copy.frozen_at is None
    assert copy.created_at == LATER


def test_to_load_plan_for_request_family_has_no_ramp_steps():
    plan = to_load_plan(
        _profile(), plan_id="plan-1", target_authorization_confirmed=True
    )

    assert isinstance(plan, LoadPlan)
    assert plan.ramp_steps == ()
    assert plan.target_authorization_confirmed is True


def test_to_load_plan_for_ramp_family_derives_ramp_steps():
    ramp_profile = _profile(
        family=TestFamily.RAMP,
        level=IntensityLevel.MOYEN,
        duration=Duration(minutes=3),
    )

    plan = to_load_plan(ramp_profile, plan_id="plan-2", target_authorization_confirmed=True)

    assert len(plan.ramp_steps) == 2
