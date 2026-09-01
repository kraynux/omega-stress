import pytest

from omega_stress.core.enums import DurationPresetId, TestFamily
from omega_stress.domain.load.duration_presets import (
    DURATION_PRESETS,
    build_duration_preset_ramp_steps,
    duration_preset,
)


@pytest.mark.parametrize("preset_id", list(DurationPresetId))
def test_every_preset_id_has_a_preset(preset_id):
    assert preset_id in DURATION_PRESETS
    assert duration_preset(preset_id).id is preset_id


@pytest.mark.parametrize("preset_id", list(DurationPresetId))
def test_split_sums_to_total_minutes(preset_id):
    preset = duration_preset(preset_id)
    split = preset.split

    total_seconds = split.warmup_seconds + split.ramp_seconds + split.plateau_seconds + (
        split.cooldown_seconds
    )

    assert total_seconds == preset.total_minutes * 60


@pytest.mark.parametrize("preset_id", list(DurationPresetId))
def test_build_ramp_steps_produces_four_valid_steps(preset_id):
    preset = duration_preset(preset_id)

    steps = build_duration_preset_ramp_steps(preset)

    assert len(steps) == 4
    assert [s.order for s in steps] == [1, 2, 3, 4]
    # warm-up : pas de charge ; rampe : montee lineaire ; plateau : plein
    # regime ; retour au calme : descente lineaire.
    assert (steps[0].start_ratio, steps[0].end_ratio) == (0.0, 0.0)
    assert (steps[1].start_ratio, steps[1].end_ratio) == (0.0, 1.0)
    assert (steps[2].start_ratio, steps[2].end_ratio) == (1.0, 1.0)
    assert (steps[3].start_ratio, steps[3].end_ratio) == (1.0, 0.0)


def test_d6_soak_excludes_request_family():
    preset = duration_preset(DurationPresetId.D6)

    assert TestFamily.REQUEST not in preset.compatible_families
    assert TestFamily.CONNECTION in preset.compatible_families
    assert TestFamily.RAMP in preset.compatible_families


@pytest.mark.parametrize("preset_id", [DurationPresetId.D1, DurationPresetId.D2])
def test_short_presets_never_require_reinforced_confirmation(preset_id):
    assert duration_preset(preset_id).reinforced_level is None


def test_d3_standard_has_no_reinforced_tier_either():
    # D3 exclut simplement Maximum, sans palier renforce (a la difference
    # de D4/D5/D6 qui en proposent un).
    assert duration_preset(DurationPresetId.D3).reinforced_level is None
