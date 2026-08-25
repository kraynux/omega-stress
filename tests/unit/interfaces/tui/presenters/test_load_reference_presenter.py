from omega_stress.core.enums import TestFamily
from omega_stress.interfaces.tui.presenters.load_reference_presenter import (
    load_reference_family_note,
    load_reference_rows,
)


def test_load_reference_rows_covers_every_family_and_level():
    rows = load_reference_rows()

    assert len(rows) == 12
    assert {row.test_type for row in rows} == {"Test requetes", "Test connexions", "Test charge"}
    assert {row.level for row in rows} == {"Bas", "Moyen", "Haut", "Maximum"}


def test_precheck_marked_only_for_haut_and_maximum():
    rows = load_reference_rows()

    for row in rows:
        expected = "Oui" if row.level in {"Haut", "Maximum"} else "Non"
        assert row.precheck == expected


def test_duration_label_mentions_precheck_only_when_it_unlocks_a_longer_duration():
    rows = load_reference_rows()

    bas_row = next(r for r in rows if r.test_type == "Test requetes" and r.level == "Bas")
    assert bas_row.durations == "1 a 5 min"

    haut_row = next(r for r in rows if r.test_type == "Test requetes" and r.level == "Haut")
    assert "pre-check" in haut_row.durations
    assert "5 min" in haut_row.durations


def test_request_row_target_matches_requests_per_minute():
    rows = load_reference_rows()

    maximum_request_row = next(
        r for r in rows if r.test_type == "Test requetes" and r.level == "Maximum"
    )
    assert maximum_request_row.target == "2000 req/min"
    assert maximum_request_row.burst == "~33 req/s en rafale"


def test_connection_row_target_matches_concurrent_connections():
    rows = load_reference_rows()

    maximum_connection_row = next(
        r for r in rows if r.test_type == "Test connexions" and r.level == "Maximum"
    )
    assert maximum_connection_row.target == "200 connexions"
    assert maximum_connection_row.burst == "200 en parallele, chaque seconde"


def test_family_notes_are_distinct_per_family():
    request_note = load_reference_family_note(TestFamily.REQUEST)
    connection_note = load_reference_family_note(TestFamily.CONNECTION)
    ramp_note = load_reference_family_note(TestFamily.RAMP)

    assert request_note != connection_note != ramp_note
    assert "debit" in request_note.lower()
    assert "simultaneite" in connection_note.lower()
    assert "pic" in ramp_note.lower()
