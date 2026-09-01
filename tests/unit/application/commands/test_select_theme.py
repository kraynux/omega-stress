from omega_lib.terminal.models import RenderProfile

from omega_stress.application.commands.select_theme import select_theme
from tests.fixtures.fakes import FakeSettingsStore


def test_selects_and_persists_known_theme():
    store = FakeSettingsStore()

    dto = select_theme("omega-neon", render_profile=RenderProfile.COMPLETE, settings_store=store)

    assert dto.theme_name == "omega-neon"
    assert dto.fell_back_from is None
    assert store.get("theme") == "omega-neon"


def test_unknown_theme_falls_back_and_persists_the_fallback():
    store = FakeSettingsStore()

    dto = select_theme(
        "does-not-exist", render_profile=RenderProfile.COMPLETE, settings_store=store
    )

    assert dto.theme_name == "omega-base"
    assert dto.fell_back_from == "does-not-exist"
    assert store.get("theme") == "omega-base"
