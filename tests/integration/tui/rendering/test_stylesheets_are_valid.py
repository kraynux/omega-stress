import pytest
from omega_lib.terminal.models import RenderProfile
from textual.app import App
from textual.geometry import Spacing
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


@pytest.mark.parametrize("profile", ALL_PROFILES)
async def test_omega_panel_border_is_uniform_across_render_profiles(profile):
    """Regression : chaque profil (complete/standard/reduced/mono.tcss)
    redefinissait sa PROPRE bordure/padding/fond pour ".omega-panel",
    chargee APRES styles/terminal_frame.tcss (cadre "application"
    reutilisable) dans stylesheet_paths_for() - la masquant
    silencieusement partout SAUF sur l'ecran d'accueil (".omega-home-root",
    jamais touche par aucun profil). Retour utilisateur : "j'ai que le
    menu principal avec la bordure" - prouve ici que les 4 profils
    resolvent desormais IDENTIQUEMENT vers le cadre defini par
    terminal_frame.tcss, plutot que de re-verifier au cas par cas."""
    paths = load_paths_for(profile)

    class _ProbeApp(App):
        CSS_PATH = paths

        def compose(self):
            yield Static("probe", classes="omega-panel")

    app = _ProbeApp()
    async with app.run_test():
        widget = app.query_one(Static)
        assert widget.styles.border_top[0] == "solid"
        assert widget.styles.padding == Spacing(top=1, right=2, bottom=1, left=2)
