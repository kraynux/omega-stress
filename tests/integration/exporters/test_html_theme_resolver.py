from omega_stress.domain.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from omega_stress.infrastructure.exporters.html_theme_resolver import resolve_export_palette


def test_known_theme_resolves_to_its_palette():
    assert resolve_export_palette("omega-burn") == EXPORT_PALETTES["omega-burn"]


def test_unknown_theme_falls_back_to_default():
    assert resolve_export_palette("does-not-exist") == EXPORT_PALETTES[DEFAULT_EXPORT_THEME]
