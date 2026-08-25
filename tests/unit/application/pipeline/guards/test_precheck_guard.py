import pytest

from omega_stress.application.pipeline.guards.precheck_guard import check_precheck
from omega_stress.core.enums import IntensityLevel
from omega_stress.core.results import Err, Ok


@pytest.mark.parametrize("level", [IntensityLevel.BAS, IntensityLevel.MOYEN])
def test_bas_moyen_never_require_precheck(level):
    assert isinstance(check_precheck(level, precheck_validated=False), Ok)


@pytest.mark.parametrize("level", [IntensityLevel.HAUT, IntensityLevel.MAXIMUM])
def test_haut_maximum_denied_without_precheck(level):
    assert isinstance(check_precheck(level, precheck_validated=False), Err)


@pytest.mark.parametrize("level", [IntensityLevel.HAUT, IntensityLevel.MAXIMUM])
def test_haut_maximum_authorized_with_precheck(level):
    assert isinstance(check_precheck(level, precheck_validated=True), Ok)
