from omega_stress.domain.theme.policies import (
    DEFAULT_EXPORT_THEME,
    DEFAULT_TUI_THEME,
    EXPORT_PALETTES,
    TUI_THEMES,
    degrade_to_grayscale,
    mono_palette,
    reduced_palette,
)


def test_catalog_has_ten_tui_themes():
    assert len(TUI_THEMES) == 10


def test_catalog_has_five_export_palettes():
    assert len(EXPORT_PALETTES) == 5


def test_default_themes_exist_in_their_catalog():
    assert DEFAULT_TUI_THEME in TUI_THEMES
    assert DEFAULT_EXPORT_THEME in EXPORT_PALETTES


def test_omega_mono_and_minimal_use_named_ansi_colors_not_hex():
    for name in ("omega-mono", "omega-minimal"):
        palette = TUI_THEMES[name].palette
        assert not palette.background.startswith("#")
        assert not palette.accent.startswith("#")


def test_degrade_to_grayscale_preserves_black_and_white():
    assert degrade_to_grayscale("#000000") == "#000000"
    assert degrade_to_grayscale("#ffffff") == "#ffffff"


def test_degrade_to_grayscale_matches_perceptual_luminance_formula():
    # #00d4ff -> r=0 g=212 b=255 -> Y = 0.2126*0 + 0.7152*212 + 0.0722*255 ~ 170
    assert degrade_to_grayscale("#00d4ff") == "#aaaaaa"


def test_degrade_to_grayscale_leaves_named_colors_unchanged():
    assert degrade_to_grayscale("white") == "white"
    assert degrade_to_grayscale("bright_black") == "bright_black"


def test_reduced_palette_flattens_surface_and_panel_onto_background():
    original = TUI_THEMES["omega-base"].palette

    reduced = reduced_palette(original)

    assert reduced.background == original.background
    assert reduced.surface == original.background
    assert reduced.panel == original.background
    assert reduced.accent == original.accent
    assert reduced.foreground == original.foreground


def test_mono_palette_converts_hex_theme_to_grayscale():
    original = TUI_THEMES["omega-base"].palette

    mono = mono_palette(original)

    for value in (mono.background, mono.surface, mono.panel, mono.foreground, mono.accent):
        assert value.startswith("#")
        r, g, b = value[1:3], value[3:5], value[5:7]
        assert r == g == b  # niveau de gris : les trois canaux sont egaux


def test_mono_palette_leaves_already_neutral_theme_unchanged():
    original = TUI_THEMES["omega-mono"].palette

    mono = mono_palette(original)

    assert mono == original
