from omega_stress.core.enums import DurationPresetId, IntensityLevel, TestFamily
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.duration_presets import (
    build_duration_preset_ramp_steps,
    duration_preset,
)
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.presets import fixed_rate_preset, ramp_preset
from omega_stress.infrastructure.runner.engine_params import target_for_interval, total_intervals


def _plan(**overrides) -> LoadPlan:
    defaults = dict(
        id="plan-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=2),
        thresholds=Thresholds(max_error_rate=0.5),
        target_authorization_confirmed=True,
    )
    defaults.update(overrides)
    return LoadPlan(**defaults)


def test_total_intervals_matches_duration_in_seconds():
    assert total_intervals(_plan(duration=Duration(minutes=1))) == 60
    assert total_intervals(_plan(duration=Duration(minutes=3))) == 180


def test_request_family_target_matches_preset():
    plan = _plan(family=TestFamily.REQUEST, level=IntensityLevel.MOYEN)
    preset = fixed_rate_preset(IntensityLevel.MOYEN)

    target = target_for_interval(plan, 0)

    assert target.requests_per_second == preset.requests_per_minute / 60.0
    assert target.concurrency == 0


def test_connection_family_target_uses_concurrency_not_rate():
    plan = _plan(family=TestFamily.CONNECTION, level=IntensityLevel.HAUT)
    preset = fixed_rate_preset(IntensityLevel.HAUT)

    target = target_for_interval(plan, 0)

    assert target.requests_per_second == 0.0
    assert target.concurrency == preset.concurrent_connections


def test_ramp_family_starts_at_zero_and_reaches_peak():
    level = IntensityLevel.BAS
    preset = ramp_preset(level)
    steps = build_ramp_steps(
        level, duration_minutes=preset.ramp_up_minutes + preset.plateau_minutes_min
    )
    plan = _plan(family=TestFamily.RAMP, level=level, ramp_steps=steps)

    first_interval = target_for_interval(plan, 0)
    ramp_up_seconds = int(steps[0].duration_minutes * 60)
    plateau_interval = target_for_interval(plan, ramp_up_seconds + 5)

    assert first_interval.requests_per_second == 0.0
    assert plateau_interval.requests_per_second == preset.peak_requests_per_minute / 60.0


def test_connection_family_follows_ramp_steps_when_present():
    # Mode "profil" D1-D6 (2026-09-01) : quand ramp_steps est peuple pour
    # une famille Connexions, la concurrence suit desormais le ratio de
    # phase (warm-up/rampe/plateau/retour au calme) au lieu de rester
    # plate — non-regression : sans ramp_steps, voir le test flat ci-dessus.
    level = IntensityLevel.BAS
    d1 = duration_preset(DurationPresetId.D1)
    steps = build_duration_preset_ramp_steps(d1)
    plan = _plan(
        family=TestFamily.CONNECTION,
        level=level,
        duration=Duration(minutes=d1.total_minutes),
        duration_preset_id=DurationPresetId.D1,
        ramp_steps=steps,
    )
    preset = fixed_rate_preset(level)

    warmup_interval = target_for_interval(plan, 0)
    plateau_second = d1.split.warmup_seconds + d1.split.ramp_seconds + 5
    plateau_interval = target_for_interval(plan, plateau_second)

    assert warmup_interval.concurrency == 0
    assert plateau_interval.concurrency == preset.concurrent_connections


def test_ramp_target_beyond_last_step_holds_final_ratio():
    level = IntensityLevel.BAS
    preset = ramp_preset(level)
    steps = build_ramp_steps(
        level, duration_minutes=preset.ramp_up_minutes + preset.plateau_minutes_min
    )
    plan = _plan(family=TestFamily.RAMP, level=level, ramp_steps=steps)

    far_future = target_for_interval(plan, 100_000)

    assert far_future.requests_per_second == preset.peak_requests_per_minute / 60.0
