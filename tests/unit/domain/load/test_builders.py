import pytest

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.presets import ramp_preset

ALL_LEVELS = list(IntensityLevel)


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_build_ramp_steps_returns_ramp_up_then_plateau(level):
    steps = build_ramp_steps(level)

    assert len(steps) == 2
    ramp_up, plateau = steps
    assert ramp_up.order == 1
    assert ramp_up.start_ratio == 0.0
    assert ramp_up.end_ratio == 1.0
    assert plateau.order == 2
    assert plateau.start_ratio == 1.0
    assert plateau.end_ratio == 1.0


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_ramp_step_durations_match_preset(level):
    preset = ramp_preset(level)
    ramp_up, plateau = build_ramp_steps(level)

    assert ramp_up.duration_minutes == preset.ramp_up_minutes
    assert plateau.duration_minutes == preset.plateau_minutes_min
