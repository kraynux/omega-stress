from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.errors import (
    PrecheckRequiredError,
    UnauthorizedTargetError,
    ValidationError,
)
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.validators import evaluate_threshold, validate_plan


def _plan(**overrides):
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


def test_valid_plan_passes():
    result = validate_plan(_plan())

    assert isinstance(result, Ok)


def test_unconfirmed_authorization_is_rejected():
    result = validate_plan(_plan(target_authorization_confirmed=False))

    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedTargetError)


def test_haut_without_precheck_is_rejected():
    result = validate_plan(
        _plan(level=IntensityLevel.HAUT, duration=Duration(minutes=1), precheck_validated=False)
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, PrecheckRequiredError)


def test_haut_with_precheck_and_extended_duration_passes():
    result = validate_plan(
        _plan(level=IntensityLevel.HAUT, duration=Duration(minutes=5), precheck_validated=True)
    )

    assert isinstance(result, Ok)


def test_disallowed_duration_is_rejected_even_with_precheck():
    # 2 min n'est jamais un choix ferme pour Haut/Maximum, meme avec
    # pre-check valide (qui n'autorise que l'ajout de 5 min, pas une
    # valeur libre) : isole ici le rejet par duree, en passant d'abord le
    # guard de pre-check pour ne pas le confondre avec
    # test_haut_without_precheck_is_rejected ci-dessus.
    result = validate_plan(
        _plan(level=IntensityLevel.HAUT, duration=Duration(minutes=2), precheck_validated=True)
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)


def test_ramp_family_requires_ramp_steps():
    result = validate_plan(_plan(family=TestFamily.RAMP, ramp_steps=()))

    assert isinstance(result, Err)


def test_non_ramp_family_rejects_ramp_steps():
    steps = build_ramp_steps(IntensityLevel.BAS)
    result = validate_plan(_plan(family=TestFamily.REQUEST, ramp_steps=steps))

    assert isinstance(result, Err)


def test_ramp_family_with_steps_passes():
    steps = build_ramp_steps(IntensityLevel.BAS)
    result = validate_plan(_plan(family=TestFamily.RAMP, ramp_steps=steps))

    assert isinstance(result, Ok)


def test_evaluate_threshold_passes_within_bounds():
    thresholds = Thresholds(max_error_rate=0.1, max_p95_latency_ms=500)

    result = evaluate_threshold(
        observed_error_rate=0.05, observed_p95_latency_ms=300, thresholds=thresholds
    )

    assert isinstance(result, Ok)


def test_evaluate_threshold_flags_error_rate_breach():
    thresholds = Thresholds(max_error_rate=0.1)

    result = evaluate_threshold(
        observed_error_rate=0.2, observed_p95_latency_ms=None, thresholds=thresholds
    )

    assert isinstance(result, Err)


def test_evaluate_threshold_flags_latency_breach():
    thresholds = Thresholds(max_error_rate=0.5, max_p95_latency_ms=200)

    result = evaluate_threshold(
        observed_error_rate=0.0, observed_p95_latency_ms=250, thresholds=thresholds
    )

    assert isinstance(result, Err)
