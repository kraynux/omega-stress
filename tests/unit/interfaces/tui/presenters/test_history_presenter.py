from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.interfaces.tui.presenters.history_presenter import (
    most_recent_first,
)


def _run(run_id: str, started_at: str) -> RunDTO:
    return RunDTO(
        id=run_id,
        profile_id=None,
        target_id="target-1",
        target_address="https://example.org/",
        family="request",
        level="moyen",
        started_at=started_at,
        finished_at=None,
        verdict=None,
        observed_rate_per_minute=None,
        p95_latency_ms=None,
        error_count=None,
        total_requests=None,
    )


def test_orders_by_started_at_descending():
    older = _run("older", "2026-08-20T10:00:00")
    newer = _run("newer", "2026-08-24T10:00:00")

    ordered = most_recent_first((older, newer))

    assert [r.id for r in ordered] == ["newer", "older"]
