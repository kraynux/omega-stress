import pytest

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.presets import (
    FIXED_RATE_PRESETS,
    RAMP_PRESETS,
    fixed_rate_preset,
    ramp_preset,
)

ALL_LEVELS = list(IntensityLevel)


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_every_intensity_level_has_a_fixed_rate_preset(level):
    assert level in FIXED_RATE_PRESETS


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_every_intensity_level_has_a_ramp_preset(level):
    assert level in RAMP_PRESETS


@pytest.mark.parametrize(
    ("level", "requests_per_minute", "connections"),
    [
        (IntensityLevel.FAIBLE, 250, 25),
        (IntensityLevel.BAS, 500, 50),
        (IntensityLevel.MOYEN, 1000, 100),
        (IntensityLevel.HAUT, 2000, 200),
        (IntensityLevel.PUISSANT, 6000, 1000),
        (IntensityLevel.AGRESSIF, 10000, 2000),
        (IntensityLevel.VIOLENT, 15000, 3500),
        (IntensityLevel.MAXIMUM, 20000, 5000),
    ],
)
def test_fixed_rate_values_match_product_spec(level, requests_per_minute, connections):
    preset = fixed_rate_preset(level)

    assert preset.requests_per_minute == requests_per_minute
    assert preset.concurrent_connections == connections


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_ramp_peak_matches_fixed_rate_at_same_level(level):
    """Meme echelle, deux representations : les pics de rampe doivent
    reprendre exactement les valeurs du palier fixe au meme niveau."""
    fixed = fixed_rate_preset(level)
    ramp = ramp_preset(level)

    assert ramp.peak_requests_per_minute == fixed.requests_per_minute
    assert ramp.peak_connections == fixed.concurrent_connections
