from omega_stress.application.pipeline.planner import prepare_plan
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds


def _plan(**overrides) -> LoadPlan:
    defaults = dict(
        id="plan-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.1),
        target_authorization_confirmed=True,
        precheck_validated=False,
        ramp_steps=(),
    )
    defaults.update(overrides)
    return LoadPlan(**defaults)


def test_valid_plan_passes_through():
    result = prepare_plan(_plan())

    assert isinstance(result, Ok)


def test_invalid_plan_is_rejected():
    result = prepare_plan(_plan(target_authorization_confirmed=False))

    assert isinstance(result, Err)
