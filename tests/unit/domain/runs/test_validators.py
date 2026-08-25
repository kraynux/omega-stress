from datetime import datetime, timezone

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.runs.models import LoadRun
from omega_stress.domain.runs.validators import can_be_replayed, validate_run_timing

STARTED = datetime(2026, 8, 23, 10, 0, tzinfo=timezone.utc)


def _run(**overrides):
    defaults = dict(
        id="run-1",
        profile_id="profile-1",
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
    )
    defaults.update(overrides)
    return LoadRun(**defaults)


def test_timing_valid_for_ongoing_run():
    assert isinstance(validate_run_timing(_run()), Ok)


def test_timing_valid_when_finished_after_started():
    finished = _run(finished_at=datetime(2026, 8, 23, 10, 5, tzinfo=timezone.utc))
    assert isinstance(validate_run_timing(finished), Ok)


def test_timing_invalid_when_finished_before_started():
    broken = _run(finished_at=datetime(2026, 8, 23, 9, 0, tzinfo=timezone.utc))
    assert isinstance(validate_run_timing(broken), Err)


def test_can_be_replayed_true_with_profile():
    assert can_be_replayed(_run(profile_id="profile-1")) is True


def test_can_be_replayed_false_without_profile():
    assert can_be_replayed(_run(profile_id=None)) is False
