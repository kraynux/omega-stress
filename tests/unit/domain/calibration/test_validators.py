from omega_stress.core.results import Err, Ok
from omega_stress.domain.calibration import policies
from omega_stress.domain.calibration.validators import (
    compute_envelope,
    evaluate_preconditions,
    evaluate_stage_outcome,
)
from omega_stress.domain.runs.models import SystemSnapshot

_STAGE = policies.CALIBRATION_STAGES[1]  # calib_1 : 25 VU, 100 RPS, 10s


def _samples(cpu_generator=10.0, cpu_global=10.0, memory=80.0, cores=4, count=3):
    return [
        SystemSnapshot(
            cpu_percent_generator=cpu_generator,
            cpu_percent_global=cpu_global,
            memory_available_percent=memory,
            logical_cpu_count=cores,
        )
        for _ in range(count)
    ]


# --- evaluate_preconditions() ---


def test_preconditions_pass_when_machine_is_idle():
    result = evaluate_preconditions(
        cpu_global_percent=5.0,
        memory_available_percent=80.0,
        swap_active_or_growing=False,
        load_average_1min=0.5,
        logical_cpu_count=4,
        another_calibration_or_run_active=False,
    )

    assert isinstance(result, Ok)


def test_preconditions_reject_when_another_calibration_active():
    result = evaluate_preconditions(
        cpu_global_percent=5.0,
        memory_available_percent=80.0,
        swap_active_or_growing=False,
        load_average_1min=0.5,
        logical_cpu_count=4,
        another_calibration_or_run_active=True,
    )

    assert isinstance(result, Err)


def test_preconditions_reject_high_cpu():
    # Seuil releve a 70.0 le 2026-09-01 (bug reel) : 80.0 depasse encore.
    result = evaluate_preconditions(
        cpu_global_percent=80.0,
        memory_available_percent=80.0,
        swap_active_or_growing=False,
        load_average_1min=0.5,
        logical_cpu_count=4,
        another_calibration_or_run_active=False,
    )

    assert isinstance(result, Err)


def test_preconditions_reject_low_memory():
    result = evaluate_preconditions(
        cpu_global_percent=5.0,
        memory_available_percent=10.0,
        swap_active_or_growing=False,
        load_average_1min=0.5,
        logical_cpu_count=4,
        another_calibration_or_run_active=False,
    )

    assert isinstance(result, Err)


def test_preconditions_reject_growing_swap():
    result = evaluate_preconditions(
        cpu_global_percent=5.0,
        memory_available_percent=80.0,
        swap_active_or_growing=True,
        load_average_1min=0.5,
        logical_cpu_count=4,
        another_calibration_or_run_active=False,
    )

    assert isinstance(result, Err)


def test_preconditions_reject_high_load_average():
    result = evaluate_preconditions(
        cpu_global_percent=5.0,
        memory_available_percent=80.0,
        swap_active_or_growing=False,
        load_average_1min=8.0,
        logical_cpu_count=4,
        another_calibration_or_run_active=False,
    )

    assert isinstance(result, Err)


def test_preconditions_tolerate_missing_measurements():
    # Une mesure non disponible (None) ne doit jamais bloquer le
    # calibrage a elle seule.
    result = evaluate_preconditions(
        cpu_global_percent=None,
        memory_available_percent=None,
        swap_active_or_growing=False,
        load_average_1min=None,
        logical_cpu_count=4,
        another_calibration_or_run_active=False,
    )

    assert isinstance(result, Ok)


# --- evaluate_stage_outcome() : sante ---


def test_stage_is_healthy_within_all_thresholds():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.is_healthy is True
    assert result.stop_reason is None


def test_stage_unhealthy_when_rps_ratio_too_low_but_no_stop():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=50.0,  # 50% du RPS cible, < 85% de sante
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.is_healthy is False
    assert result.stop_reason is None  # un seul palier isole, pas d'arret


# --- evaluate_stage_outcome() : arret ---


def test_stage_stops_on_sustained_generator_and_global_cpu_together():
    # 4 coeurs : seuil d'arret generateur = 0.95 * (100/4) = 23.75% ; ET
    # doit AUSSI depasser le seuil global (90%) — 2026-09-01, second
    # correctif : le CPU generateur seul ne suffit plus (voir policies.py).
    samples = _samples(cpu_generator=25.0, cpu_global=95.0, cores=4, count=3)
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=samples,
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason == "generator_cpu_sustained"
    assert result.is_healthy is False


def test_stage_does_not_stop_on_sustained_generator_cpu_alone():
    # Bug reel corrige le 2026-09-01 : un calibrage normal sature
    # legitimement ~20-25% de CPU generateur sur une machine 4 coeurs
    # saine — ne doit plus jamais arreter un palier a lui seul si le
    # reste de la machine (CPU global) n'est pas aussi sous pression.
    samples = _samples(cpu_generator=25.0, cpu_global=10.0, cores=4, count=3)
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=samples,
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason is None


def test_stage_does_not_stop_on_sustained_global_cpu_alone():
    # Symetrique : un CPU machine eleve pour une raison EXTERIEURE au
    # calibrage ne doit pas non plus, a lui seul, arreter un palier.
    samples = _samples(cpu_generator=5.0, cpu_global=95.0, count=3)
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=samples,
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason is None


def test_stage_does_not_stop_on_isolated_generator_cpu_spike():
    samples = [
        SystemSnapshot(cpu_percent_generator=25.0, cpu_percent_global=95.0, logical_cpu_count=4),
        SystemSnapshot(cpu_percent_generator=5.0, cpu_percent_global=95.0, logical_cpu_count=4),
        SystemSnapshot(cpu_percent_generator=25.0, cpu_percent_global=95.0, logical_cpu_count=4),
    ]
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=samples,
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason is None


def test_stage_stops_on_low_available_memory():
    samples = _samples(memory=10.0, count=1)
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=samples,
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason == "memory_available_low"


def test_stage_stops_on_high_error_rate():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.02,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason == "error_rate_high"


def test_stage_stops_on_consecutive_timeouts():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=policies.CALIBRATION_STOP_CONSECUTIVE_TIMEOUTS,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason == "consecutive_timeouts"


def test_stage_stops_on_two_consecutive_low_rps_stages():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=50.0,
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=True,
    )

    assert result.stop_reason == "rps_achieved_low_consecutive_stages"


def test_stage_does_not_stop_on_single_low_rps_stage():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=50.0,
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason is None


def test_stage_missing_system_snapshot_never_stops_or_raises():
    result = evaluate_stage_outcome(
        _STAGE,
        rps_achieved=95.0,
        error_rate=0.0,
        system_samples=[],
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    assert result.stop_reason is None
    assert result.is_healthy is True


# --- compute_envelope() ---


def test_compute_envelope_returns_none_when_no_stage_was_healthy():
    assert compute_envelope([], first_degraded_stage_id="idle_baseline") is None


def test_compute_envelope_applies_safety_margin():
    healthy = [
        evaluate_stage_outcome(
            policies.CALIBRATION_STAGES[2],  # calib_2 : 100 VU, 500 RPS
            rps_achieved=500.0,
            error_rate=0.0,
            system_samples=_samples(),
            consecutive_timeouts=0,
            previous_stage_rps_below_ratio=False,
        )
    ]

    envelope = compute_envelope(healthy, first_degraded_stage_id=None)

    assert envelope is not None
    assert envelope.vu_safe == int(100 * policies.CALIBRATION_SAFETY_MARGIN)
    assert envelope.rps_safe == int(500.0 * policies.CALIBRATION_SAFETY_MARGIN)
    assert envelope.connections_safe == envelope.vu_safe
    assert envelope.last_healthy_stage_id == "calib_2"


def test_compute_envelope_confidence_increases_with_stage_reached():
    early = evaluate_stage_outcome(
        policies.CALIBRATION_STAGES[1],  # calib_1
        rps_achieved=100.0,
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )
    late = evaluate_stage_outcome(
        policies.CALIBRATION_STAGES[4],  # calib_4
        rps_achieved=3000.0,
        error_rate=0.0,
        system_samples=_samples(),
        consecutive_timeouts=0,
        previous_stage_rps_below_ratio=False,
    )

    early_envelope = compute_envelope([early], first_degraded_stage_id=None)
    late_envelope = compute_envelope([early, late], first_degraded_stage_id=None)

    assert early_envelope is not None
    assert late_envelope is not None
    assert early_envelope.confidence == "faible"
    assert late_envelope.confidence == "elevee"
