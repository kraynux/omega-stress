from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.domain.theme.policies import EXPORT_PALETTES, TUI_THEMES
from omega_stress.interfaces.tui.presenters.theme_presenter import (
    available_export_theme_names,
    available_theme_names,
    status_label,
)


def test_available_theme_names_lists_the_full_catalog():
    names = available_theme_names()

    assert len(names) == 10
    assert set(names) == set(TUI_THEMES.keys())


def test_available_export_theme_names_lists_the_export_catalog_only():
    names = available_export_theme_names()

    assert len(names) == 5
    assert set(names) == set(EXPORT_PALETTES.keys())
    # Catalogues independants (voir domain/theme/policies.py) : les noms
    # export-only doivent apparaitre, et le catalogue TUI ne doit pas
    # fuiter ici (regression du bug 2026-08-27 : export_dialog.py
    # proposait a tort le catalogue TUI_THEMES pour le theme d'export).
    assert "light-basic" in names
    assert "light-alt" in names
    assert "omega-dark" not in names


def test_status_label_without_fallback():
    status = ThemeStatusDTO(
        theme_name="omega-neon", render_profile="complete", fell_back_from=None
    )

    assert status_label(status) == "omega-neon"


def test_status_label_mentions_fallback():
    status = ThemeStatusDTO(
        theme_name="omega-base", render_profile="complete", fell_back_from="omega-inconnu"
    )

    assert status_label(status) == "omega-base (repli depuis omega-inconnu)"
