from omega_stress.core.enums import RenderProfile
from omega_stress.domain.theme.policies import DEFAULT_TUI_THEME, TUI_THEMES
from omega_stress.domain.theme.service import resolve_applied_theme, resolve_palette


def test_known_theme_applies_without_fallback():
    applied = resolve_applied_theme("omega-neon", render_profile=RenderProfile.COMPLETE)

    assert applied.theme_name == "omega-neon"
    assert applied.fell_back_from is None


def test_unknown_theme_falls_back_to_default():
    applied = resolve_applied_theme("does-not-exist", render_profile=RenderProfile.COMPLETE)

    assert applied.theme_name == DEFAULT_TUI_THEME
    assert applied.fell_back_from == "does-not-exist"


def test_resolve_palette_complete_returns_theme_palette_unchanged():
    palette = resolve_palette("omega-base", RenderProfile.COMPLETE)

    assert palette == TUI_THEMES["omega-base"].palette


def test_resolve_palette_reduced_flattens_surface_and_panel():
    palette = resolve_palette("omega-base", RenderProfile.REDUCED)

    assert palette.surface == palette.background
    assert palette.panel == palette.background


def test_resolve_palette_mono_is_grayscale():
    palette = resolve_palette("omega-neon", RenderProfile.MONO)

    for value in (palette.background, palette.accent):
        assert value.startswith("#")
        r, g, b = value[1:3], value[3:5], value[5:7]
        assert r == g == b
