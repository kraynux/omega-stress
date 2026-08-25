from omega_stress.application.dto.theme_dto import ThemeStatusDTO
from omega_stress.domain.theme.policies import TUI_THEMES
from omega_stress.interfaces.tui.presenters.theme_presenter import (
    available_theme_names,
    status_label,
)


def test_available_theme_names_lists_the_full_catalog():
    names = available_theme_names()

    assert len(names) == 10
    assert set(names) == set(TUI_THEMES.keys())


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
