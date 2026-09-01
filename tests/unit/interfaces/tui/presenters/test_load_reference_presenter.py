from omega_stress.core.enums import TestFamily
from omega_stress.interfaces.tui.presenters.load_reference_presenter import (
    load_reference_family_note,
    load_reference_rows,
)


def test_load_reference_rows_covers_every_family_and_level():
    rows = load_reference_rows()

    assert len(rows) == 24
    assert {row.test_type for row in rows} == {"Test requetes", "Test connexions", "Test charge"}
    assert {row.level for row in rows} == {
        "Faible",
        "Bas",
        "Moyen",
        "Haut",
        "Puissant",
        "Agressif",
        "Violent",
        "Maximum",
    }


def test_precheck_marked_per_tier():
    rows = load_reference_rows()

    never_gated = {"Faible", "Bas", "Moyen", "Haut"}
    gated_optional = {"Puissant", "Agressif"}
    gated_mandatory = {"Violent", "Maximum"}

    for row in rows:
        if row.level in never_gated:
            assert row.precheck == "Non"
        elif row.level in gated_optional:
            assert row.precheck == "Non/Oui"
        else:
            assert row.level in gated_mandatory
            assert row.precheck == "Oui"


def test_duration_label_mentions_precheck_only_when_it_unlocks_a_longer_duration():
    rows = load_reference_rows()

    bas_row = next(r for r in rows if r.test_type == "Test requetes" and r.level == "Bas")
    assert bas_row.durations == "1 a 5 min"

    # Palier gate optionnel (Puissant) : durees de base + extension mentionnee.
    puissant_row = next(
        r for r in rows if r.test_type == "Test requetes" and r.level == "Puissant"
    )
    assert "pre-check" in puissant_row.durations
    assert "5 min" in puissant_row.durations

    # Palier gate obligatoire (Violent) : jamais d'extension, meme mention.
    violent_row = next(
        r for r in rows if r.test_type == "Test requetes" and r.level == "Violent"
    )
    assert "pre-check" not in violent_row.durations
    assert "5 min" not in violent_row.durations


def test_request_row_target_matches_requests_per_minute():
    rows = load_reference_rows()

    maximum_request_row = next(
        r for r in rows if r.test_type == "Test requetes" and r.level == "Maximum"
    )
    assert maximum_request_row.target == "20000 req/min"
    assert maximum_request_row.burst == "~333 req/s en rafale"


def test_connection_row_target_matches_concurrent_connections():
    rows = load_reference_rows()

    maximum_connection_row = next(
        r for r in rows if r.test_type == "Test connexions" and r.level == "Maximum"
    )
    assert maximum_connection_row.target == "5000 connexions"
    assert maximum_connection_row.burst == "5000 en parallele, chaque seconde"


def test_family_notes_are_distinct_per_family():
    request_note = load_reference_family_note(TestFamily.REQUEST)
    connection_note = load_reference_family_note(TestFamily.CONNECTION)
    ramp_note = load_reference_family_note(TestFamily.RAMP)

    assert request_note != connection_note != ramp_note
    assert "debit" in request_note.lower()
    assert "simultaneite" in connection_note.lower()
    assert "pic" in ramp_note.lower()
