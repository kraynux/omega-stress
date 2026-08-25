from textual.theme import Theme as TextualTheme

from omega_stress.domain.theme.policies import TUI_THEMES
from omega_stress.interfaces.tui.rendering.textual_theme_builder import (
    build_all_textual_themes,
    build_textual_theme,
    build_textual_theme_from_palette,
)


def test_builds_a_valid_theme_for_every_catalog_entry():
    themes = build_all_textual_themes()

    assert len(themes) == 10
    for theme in themes:
        assert isinstance(theme, TextualTheme)


def test_theme_name_and_polarity_match_the_definition():
    definition = TUI_THEMES["omega-neon"]

    theme = build_textual_theme(definition)

    assert theme.name == "omega-neon"
    assert theme.dark is True
    assert theme.primary == "#ff00ff"


def test_light_theme_is_not_dark():
    theme = build_textual_theme(TUI_THEMES["omega-light"])

    assert theme.dark is False


def test_build_from_palette_used_for_degraded_variants():
    palette = TUI_THEMES["omega-base"].palette

    theme = build_textual_theme_from_palette("omega-base-mono", palette, dark=True)

    assert theme.name == "omega-base-mono"
    assert theme.primary == palette.accent
