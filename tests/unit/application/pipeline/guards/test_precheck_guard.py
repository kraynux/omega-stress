import pytest

from omega_stress.application.pipeline.guards.precheck_guard import check_precheck
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok

_NEVER_GATED = [
    IntensityLevel.FAIBLE,
    IntensityLevel.BAS,
    IntensityLevel.MOYEN,
    IntensityLevel.HAUT,
]
_GATED_OPTIONAL = [IntensityLevel.PUISSANT, IntensityLevel.AGRESSIF]
_GATED_MANDATORY = [IntensityLevel.VIOLENT, IntensityLevel.MAXIMUM]


@pytest.mark.parametrize("level", _NEVER_GATED)
def test_free_tier_never_requires_precheck(level):
    assert isinstance(check_precheck(level, precheck_validated=False), Ok)


@pytest.mark.parametrize("level", _GATED_OPTIONAL)
def test_optional_tier_never_denies_without_precheck(level):
    # Different du palier obligatoire : un pre-check facultatif ne bloque
    # jamais le demarrage, il debloque seulement des durees supplementaires
    # (voir domain/load/policies.py::allowed_durations_minutes()).
    assert isinstance(check_precheck(level, precheck_validated=False), Ok)


@pytest.mark.parametrize("level", _GATED_MANDATORY)
def test_mandatory_tier_denied_without_precheck(level):
    assert isinstance(check_precheck(level, precheck_validated=False), Err)


@pytest.mark.parametrize("level", _GATED_MANDATORY)
def test_mandatory_tier_authorized_with_precheck(level):
    assert isinstance(check_precheck(level, precheck_validated=True), Ok)
