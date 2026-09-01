import pytest

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.presets import ramp_preset

ALL_LEVELS = list(IntensityLevel)


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_build_ramp_steps_returns_ramp_up_then_plateau(level):
    preset = ramp_preset(level)
    steps = build_ramp_steps(
        level, duration_minutes=preset.ramp_up_minutes + preset.plateau_minutes_min
    )

    assert len(steps) == 2
    ramp_up, plateau = steps
    assert ramp_up.order == 1
    assert ramp_up.start_ratio == 0.0
    assert ramp_up.end_ratio == 1.0
    assert plateau.order == 2
    assert plateau.start_ratio == 1.0
    assert plateau.end_ratio == 1.0


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_ramp_step_durations_match_preset_when_duration_matches_preset_total(level):
    preset = ramp_preset(level)
    preset_total = preset.ramp_up_minutes + preset.plateau_minutes_min

    ramp_up, plateau = build_ramp_steps(level, duration_minutes=preset_total)

    assert ramp_up.duration_minutes == pytest.approx(preset.ramp_up_minutes)
    assert plateau.duration_minutes == pytest.approx(preset.plateau_minutes_min)


def test_ramp_steps_are_scaled_down_to_fit_a_shorter_chosen_duration():
    # Bug reel rapporte (2026-09-01) : "1 min" choisi sur Maximum (preset :
    # 4 min de montee + 1 min de plateau = 5 min) n'explorait avant ce
    # correctif que le premier quart de la montee — desormais la montee
    # ET le plateau sont reduits proportionnellement pour tenir dans la
    # duree REELLEMENT choisie.
    preset = ramp_preset(IntensityLevel.MAXIMUM)
    assert preset.ramp_up_minutes == 4
    assert preset.plateau_minutes_min == 1

    ramp_up, plateau = build_ramp_steps(IntensityLevel.MAXIMUM, duration_minutes=1)

    assert ramp_up.duration_minutes == pytest.approx(0.8)  # 4/5 * 1
    assert plateau.duration_minutes == pytest.approx(0.2)  # 1/5 * 1
    assert ramp_up.duration_minutes + plateau.duration_minutes == pytest.approx(1.0)


def test_ramp_steps_are_scaled_up_to_fill_a_longer_chosen_duration():
    preset = ramp_preset(IntensityLevel.FAIBLE)
    preset_total = preset.ramp_up_minutes + preset.plateau_minutes_min

    ramp_up, plateau = build_ramp_steps(IntensityLevel.FAIBLE, duration_minutes=preset_total * 2)

    assert ramp_up.duration_minutes == pytest.approx(preset.ramp_up_minutes * 2)
    assert plateau.duration_minutes == pytest.approx(preset.plateau_minutes_min * 2)
