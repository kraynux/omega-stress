import pytest

from omega_stress.core.enums import RenderProfile
from omega_stress.domain.terminal.policies import (
    most_restrictive,
    render_profile_ceiling_for_size,
)


@pytest.mark.parametrize(
    ("columns", "rows", "expected"),
    [
        (200, 50, RenderProfile.COMPLETE),
        (120, 32, RenderProfile.COMPLETE),
        (119, 32, RenderProfile.STANDARD),
        (100, 28, RenderProfile.STANDARD),
        (99, 28, RenderProfile.REDUCED),
        (80, 24, RenderProfile.REDUCED),
        (79, 24, RenderProfile.MONO),
        (40, 10, RenderProfile.MONO),
    ],
)
def test_render_profile_ceiling_for_size(columns, rows, expected):
    assert render_profile_ceiling_for_size(columns, rows) is expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (RenderProfile.COMPLETE, RenderProfile.REDUCED, RenderProfile.REDUCED),
        (RenderProfile.MONO, RenderProfile.COMPLETE, RenderProfile.MONO),
        (RenderProfile.STANDARD, RenderProfile.STANDARD, RenderProfile.STANDARD),
    ],
)
def test_most_restrictive(a, b, expected):
    assert most_restrictive(a, b) is expected
    assert most_restrictive(b, a) is expected
