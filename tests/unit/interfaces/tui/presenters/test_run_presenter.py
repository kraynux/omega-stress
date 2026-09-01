from omega_stress.application.dto.run_dto import RunDTO, RunEventDTO
from omega_stress.interfaces.tui.presenters.run_presenter import (
    diagnostic_message,
    metrics_summary,
    verdict_explanation,
    verdict_label,
)


def _run(**overrides: object) -> RunDTO:
    base: dict[str, object] = dict(
        id="run-1",
        profile_id=None,
        target_id="target-1",
        target_address="https://example.org/",
        family="request",
        level="moyen",
        started_at="2026-08-24T10:00:00",
        finished_at=None,
        verdict=None,
        observed_rate_per_minute=None,
        p95_latency_ms=None,
        error_count=None,
        total_requests=None,
    )
    base.update(overrides)
    return RunDTO(**base)  # type: ignore[arg-type]


def test_verdict_label_for_in_progress_run():
    assert verdict_label(_run()) == "En cours"


def test_verdict_label_for_known_verdicts():
    assert verdict_label(_run(verdict="success")) == "Reussi"
    assert verdict_label(_run(verdict="degraded")) == "Degrade"
    assert verdict_label(_run(verdict="auto_stopped")) == "Arret automatique"
    assert verdict_label(_run(verdict="failed")) == "Echec"


def test_metrics_summary_empty_for_in_progress_run():
    assert metrics_summary(_run()) == ""


def test_metrics_summary_formats_finished_run():
    run = _run(
        verdict="success",
        observed_rate_per_minute=248.0,
        p95_latency_ms=45.0,
        error_count=1,
        total_requests=50,
    )

    summary = metrics_summary(run)

    assert "248 req/min" in summary
    assert "1/50 erreurs" in summary
    assert "p95 45 ms" in summary


def test_diagnostic_message_empty_without_events():
    assert diagnostic_message(_run()) == ""


def test_diagnostic_message_returns_the_last_event():
    run = _run(
        verdict="failed",
        events=(
            RunEventDTO(
                occurred_at="2026-08-24T10:00:00",
                kind="runner_failure",
                message="cible injoignable",
            ),
        ),
    )

    assert diagnostic_message(run) == "cible injoignable"


def test_verdict_explanation_distinguishes_manual_from_threshold_stop():
    # Bug reel rapporte (capture d'ecran) : screens/run_details.py
    # affichait "...suite a un depassement de seuil" (verdict_explanation)
    # au-dessus de "Arrete manuellement par l'utilisateur." (diagnostic_
    # message, meme run) — deux messages contradictoires sur le meme
    # ecran pour un arret manuel.
    manually_stopped = _run(
        verdict="auto_stopped",
        events=(
            RunEventDTO(
                occurred_at="2026-08-24T10:00:00",
                kind="manual_stop",
                message="Arrete manuellement par l'utilisateur.",
            ),
        ),
    )
    threshold_stopped = _run(
        verdict="auto_stopped",
        events=(
            RunEventDTO(
                occurred_at="2026-08-24T10:00:00",
                kind="generator_cpu_exceeded",
                message="CPU generateur >= 21% (~85% d'un coeur) pendant 3s",
            ),
        ),
    )

    assert "manuellement" in verdict_explanation(manually_stopped)
    assert "depassement de seuil" not in verdict_explanation(manually_stopped)
    assert "depassement de seuil" in verdict_explanation(threshold_stopped)
