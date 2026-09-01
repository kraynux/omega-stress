import pytest

from omega_stress.core.enums import IntensityLevel
from omega_stress.domain.load.policies import (
    ALWAYS_AVAILABLE_DURATIONS_MINUTES,
    GATED_BASE_DURATIONS_MINUTES,
    GATED_EXTENDED_DURATIONS_MINUTES,
    allowed_durations_minutes,
    is_precheck_available,
    is_precheck_mandatory,
    is_precheck_optional,
)

_NEVER_GATED = [
    IntensityLevel.FAIBLE,
    IntensityLevel.BAS,
    IntensityLevel.MOYEN,
    IntensityLevel.HAUT,
]
_GATED_OPTIONAL = [IntensityLevel.PUISSANT, IntensityLevel.AGRESSIF]
_GATED_MANDATORY = [IntensityLevel.VIOLENT, IntensityLevel.MAXIMUM]


@pytest.mark.parametrize("level", _NEVER_GATED)
def test_precheck_never_required_or_optional_for_the_free_tier(level):
    assert is_precheck_mandatory(level) is False
    assert is_precheck_optional(level) is False
    assert is_precheck_available(level) is False


@pytest.mark.parametrize("level", _GATED_OPTIONAL)
def test_precheck_optional_for_puissant_and_agressif(level):
    assert is_precheck_mandatory(level) is False
    assert is_precheck_optional(level) is True
    assert is_precheck_available(level) is True


@pytest.mark.parametrize("level", _GATED_MANDATORY)
def test_precheck_mandatory_for_violent_and_maximum(level):
    assert is_precheck_mandatory(level) is True
    assert is_precheck_optional(level) is False
    assert is_precheck_available(level) is True


@pytest.mark.parametrize("level", _NEVER_GATED)
def test_free_tier_durations_always_full_range(level):
    assert allowed_durations_minutes(level) == ALWAYS_AVAILABLE_DURATIONS_MINUTES
    # Une autorisation etendue ne change rien pour ces niveaux : ils ne sont
    # pas gates par le pre-check.
    assert allowed_durations_minutes(level, extended_authorized=True) == (
        ALWAYS_AVAILABLE_DURATIONS_MINUTES
    )


@pytest.mark.parametrize("level", _GATED_OPTIONAL)
def test_optional_tier_durations_gated_without_authorization(level):
    assert allowed_durations_minutes(level) == GATED_BASE_DURATIONS_MINUTES
    for extra in GATED_EXTENDED_DURATIONS_MINUTES:
        assert extra not in allowed_durations_minutes(level)


@pytest.mark.parametrize("level", _GATED_OPTIONAL)
def test_optional_tier_durations_extended_when_authorized(level):
    durations = allowed_durations_minutes(level, extended_authorized=True)

    assert durations == (*GATED_BASE_DURATIONS_MINUTES, *GATED_EXTENDED_DURATIONS_MINUTES)


@pytest.mark.parametrize("level", _GATED_MANDATORY)
def test_mandatory_tier_durations_never_extend_even_when_authorized(level):
    # Different du palier optionnel : le pre-check conditionne ici l'acces
    # au niveau lui-meme (precheck_guard.py), pas une duree supplementaire.
    without = allowed_durations_minutes(level)
    with_authorization = allowed_durations_minutes(level, extended_authorized=True)

    assert without == GATED_BASE_DURATIONS_MINUTES
    assert with_authorization == GATED_BASE_DURATIONS_MINUTES
