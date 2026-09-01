from datetime import datetime, timezone

import pytest

from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.reports.builders import build_report_content, verdict_headline
from omega_stress.domain.runs.models import LoadResult, LoadRun, RunEvent

STARTED = datetime(2026, 8, 23, 10, 0, tzinfo=timezone.utc)
FINISHED = datetime(2026, 8, 23, 10, 3, tzinfo=timezone.utc)


def _result(**overrides):
    defaults = dict(
        verdict=RunVerdict.SUCCESS,
        requested_rate_per_minute=250,
        observed_rate_per_minute=248.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        total_requests=750,
    )
    defaults.update(overrides)
    return LoadResult(**defaults)


def _run(**overrides):
    defaults = dict(
        id="run-1",
        profile_id="profile-1",
        target_id="target-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
        finished_at=FINISHED,
        result=_result(),
    )
    defaults.update(overrides)
    return LoadRun(**defaults)


def test_raises_for_unfinished_run():
    unfinished = _run(finished_at=None, result=None)

    with pytest.raises(ValueError):
        build_report_content(unfinished, target_address="https://example.org/")


def test_summary_propagates_safety_mode():
    content = build_report_content(_run(safety_mode=False), target_address="https://example.org/")

    assert content.summary.safety_mode is False


def test_builds_summary_with_computed_duration():
    content = build_report_content(_run(), target_address="https://example.org/")

    assert content.summary.run_id == "run-1"
    assert content.summary.duration_minutes == pytest.approx(3.0)


def test_success_verdict_has_no_error_recommendation():
    content = build_report_content(_run(), target_address="https://example.org/")

    assert content.diagnostic.verdict is RunVerdict.SUCCESS
    assert content.diagnostic.recommendations == ()


def test_errors_produce_a_recommendation():
    run_with_errors = _run(result=_result(error_count=5, total_requests=750))

    content = build_report_content(run_with_errors, target_address="https://example.org/")

    assert any("erreur" in rec for rec in content.diagnostic.recommendations)


def test_significant_rate_gap_flags_local_bottleneck():
    degraded = _run(
        result=_result(requested_rate_per_minute=1000, observed_rate_per_minute=500.0)
    )

    content = build_report_content(degraded, target_address="https://example.org/")

    assert any("goulot d'etranglement" in rec for rec in content.diagnostic.recommendations)


def test_minor_rate_gap_does_not_flag_bottleneck():
    fine = _run(result=_result(requested_rate_per_minute=1000, observed_rate_per_minute=950.0))

    content = build_report_content(fine, target_address="https://example.org/")

    assert content.diagnostic.recommendations == ()


def test_high_generator_cpu_peak_flags_a_recommendation():
    hot_generator = _run(result=_result(peak_cpu_percent_generator=92.0))

    content = build_report_content(hot_generator, target_address="https://example.org/")

    assert any("generateur" in rec.lower() for rec in content.diagnostic.recommendations)


def test_low_generator_cpu_peak_does_not_flag_a_recommendation():
    cool_generator = _run(result=_result(peak_cpu_percent_generator=30.0))

    content = build_report_content(cool_generator, target_address="https://example.org/")

    assert content.diagnostic.recommendations == ()


def test_no_cpu_measurement_does_not_flag_a_recommendation():
    no_measurement = _run(result=_result(peak_cpu_percent_generator=None))

    content = build_report_content(no_measurement, target_address="https://example.org/")

    assert content.diagnostic.recommendations == ()


def test_manual_stop_headline_is_distinct_from_threshold_headline():
    # Bug reel rapporte (capture d'ecran) : les deux causes d'AUTO_STOPPED
    # affichaient le meme libelle "...suite a un depassement de seuil",
    # en contradiction directe avec un diagnostic "Arrete manuellement
    # par l'utilisateur." juste en dessous.
    threshold_headline = verdict_headline(
        RunVerdict.AUTO_STOPPED, last_event_kind="generator_cpu_exceeded"
    )
    manual_headline = verdict_headline(RunVerdict.AUTO_STOPPED, last_event_kind="manual_stop")

    assert "depassement de seuil" in threshold_headline
    assert "depassement de seuil" not in manual_headline
    assert "manuellement" in manual_headline


def test_auto_stopped_headline_without_event_kind_defaults_to_threshold_wording():
    assert "depassement de seuil" in verdict_headline(RunVerdict.AUTO_STOPPED, last_event_kind=None)


def test_manually_stopped_run_shows_the_manual_headline_in_its_report():
    stopped = _run(
        result=_result(
            verdict=RunVerdict.AUTO_STOPPED,
            events=(
                RunEvent(
                    occurred_at=FINISHED,
                    kind="manual_stop",
                    message="Arrete manuellement par l'utilisateur.",
                ),
            ),
        )
    )

    content = build_report_content(stopped, target_address="https://example.org/")

    assert "manuellement" in content.diagnostic.headline
    assert "depassement de seuil" not in content.diagnostic.headline


def test_run_events_are_surfaced_as_recommendations():
    failed = _run(
        finished_at=FINISHED,
        result=_result(
            verdict=RunVerdict.FAILED,
            error_count=0,
            events=(
                RunEvent(
                    occurred_at=FINISHED, kind="runner_failure", message="cible injoignable"
                ),
            ),
        ),
    )

    content = build_report_content(failed, target_address="https://example.org/")

    assert content.diagnostic.recommendations[0] == "cible injoignable"
