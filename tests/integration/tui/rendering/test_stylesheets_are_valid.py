import pytest
from omega_lib.terminal.models import RenderProfile
from textual.app import App
from textual.widgets import Static

from omega_stress.interfaces.tui.rendering.stylesheet_loader import load_paths_for

ALL_PROFILES = list(RenderProfile)


@pytest.mark.parametrize("profile", ALL_PROFILES)
async def test_stylesheets_load_without_error(profile):
    paths = load_paths_for(profile)

    class _ProbeApp(App):
        CSS_PATH = paths

        def compose(self):
            yield Static("probe", classes="omega-panel omega-title")

    app = _ProbeApp()
    async with app.run_test():
        widget = app.query_one(Static)
        assert widget is not None
