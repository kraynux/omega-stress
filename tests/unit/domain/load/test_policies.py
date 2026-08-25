import pytest

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.policies import (
    ALWAYS_AVAILABLE_DURATIONS_MINUTES,
    GATED_DEFAULT_DURATIONS_MINUTES,
    GATED_EXTENDED_DURATION_MINUTES,
    allowed_durations_minutes,
    is_precheck_mandatory,
)


@pytest.mark.parametrize("level", [IntensityLevel.BAS, IntensityLevel.MOYEN])
def test_precheck_optional_for_bas_and_moyen(level):
    assert is_precheck_mandatory(level) is False


@pytest.mark.parametrize("level", [IntensityLevel.HAUT, IntensityLevel.MAXIMUM])
def test_precheck_mandatory_for_haut_and_maximum(level):
    assert is_precheck_mandatory(level) is True


@pytest.mark.parametrize("level", [IntensityLevel.BAS, IntensityLevel.MOYEN])
def test_bas_moyen_durations_always_full_range(level):
    assert allowed_durations_minutes(level) == ALWAYS_AVAILABLE_DURATIONS_MINUTES
    # Une autorisation etendue ne change rien pour ces niveaux : ils ne sont
    # pas gates par le pre-check.
    assert allowed_durations_minutes(level, extended_authorized=True) == (
        ALWAYS_AVAILABLE_DURATIONS_MINUTES
    )


@pytest.mark.parametrize("level", [IntensityLevel.HAUT, IntensityLevel.MAXIMUM])
def test_haut_maximum_durations_gated_without_authorization(level):
    assert allowed_durations_minutes(level) == GATED_DEFAULT_DURATIONS_MINUTES
    assert GATED_EXTENDED_DURATION_MINUTES not in allowed_durations_minutes(level)


@pytest.mark.parametrize("level", [IntensityLevel.HAUT, IntensityLevel.MAXIMUM])
def test_haut_maximum_durations_extended_when_authorized(level):
    durations = allowed_durations_minutes(level, extended_authorized=True)

    assert durations == (*GATED_DEFAULT_DURATIONS_MINUTES, GATED_EXTENDED_DURATION_MINUTES)
