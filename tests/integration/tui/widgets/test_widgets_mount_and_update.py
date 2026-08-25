from textual.app import App, ComposeResult

from omega_stress.application.dto.profile_dto import ProfileDTO
from omega_stress.application.dto.run_dto import RunDTO
from omega_stress.application.dto.target_dto import TargetDTO
from omega_stress.core.enums import RenderProfile
from omega_stress.domain.runs.models import IntervalSample
from omega_stress.interfaces.tui.widgets.authorization_checkbox import (
    AuthorizationCheckbox,
)
from omega_stress.interfaces.tui.widgets.history_table import HistoryTable
from omega_stress.interfaces.tui.widgets.load_reference_table import LoadReferenceTable
from omega_stress.interfaces.tui.widgets.notification_bar import NotificationBar
from omega_stress.interfaces.tui.widgets.profile_list import ProfileList
from omega_stress.interfaces.tui.widgets.progress_panel import ProgressPanel
from omega_stress.interfaces.tui.widgets.render_profile_badge import (
    RenderProfileBadge,
)
from omega_stress.interfaces.tui.widgets.stat_card import StatCard
from omega_stress.interfaces.tui.widgets.target_picker import TargetPicker
from omega_stress.interfaces.tui.widgets.theme_badge import ThemeBadge

_SAMPLE = IntervalSample(
    at_second=1.0,
    observed_rate_per_minute=248.0,
    p50_latency_ms=12.0,
    p95_latency_ms=45.0,
    p99_latency_ms=88.0,
    error_count=1,
    request_count=50,
)

_RUN = RunDTO(
    id="run-0000000001",
    profile_id=None,
    target_id="target-0000001",
    target_address="https://example.org/",
    family="request",
    level="moyen",
    started_at="2026-08-24T10:00:00",
    finished_at="2026-08-24T10:01:00",
    verdict="success",
    observed_rate_per_minute=248.0,
    p95_latency_ms=45.0,
    error_count=1,
    total_requests=50,
)

_PROFILE = ProfileDTO(
    id="profile-1",
    name="Palier standard",
    description="",
    default_target_id="target-0000001",
    family="request",
    level="moyen",
    duration_minutes=5,
    max_error_rate=0.05,
    max_p95_latency_ms=200.0,
    tags=(),
    extended_duration_authorized=False,
    frozen=True,
    favorite=False,
    archived=False,
    created_at="2026-08-24T09:00:00",
    frozen_at="2026-08-24T09:00:00",
)

_TARGET = TargetDTO(
    id="target-0000001",
    base_url="https://exemple.org",
    tags=(),
    notes="",
    pinned=True,
    last_used_at="2026-08-24T09:00:00",
)


async def test_stat_card_updates_its_value():
    card = StatCard("Debit observe")

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield card

    probe = _ProbeApp()
    async with probe.run_test():
        card.update_value("248 req/min")
        assert card.query_one("#value").visual.plain == "248 req/min"


async def test_progress_panel_reflects_interval_sample():
    panel = ProgressPanel()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield panel

    app = _ProbeApp()
    async with app.run_test():
        panel.update_sample(_SAMPLE)
        assert "248" in panel.query_one("#rate").query_one("#value").visual.plain
        assert "1/50" in panel.query_one("#errors").query_one("#value").visual.plain
        assert "45" in panel.query_one("#p95").query_one("#value").visual.plain


async def test_history_table_loads_run_rows():
    table = HistoryTable()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield table

    app = _ProbeApp()
    async with app.run_test():
        table.load_runs((_RUN,))
        assert table.row_count == 1


async def test_load_reference_table_loads_all_rows_on_mount():
    table = LoadReferenceTable()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield table

    app = _ProbeApp()
    async with app.run_test():
        assert table.row_count == 12


async def test_profile_list_loads_profile_rows():
    listing = ProfileList()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield listing

    app = _ProbeApp()
    async with app.run_test():
        listing.load_profiles((_PROFILE,))
        assert listing.row_count == 1


async def test_target_picker_loads_targets_and_reads_manual_value():
    picker = TargetPicker()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield picker

    app = _ProbeApp()
    async with app.run_test() as pilot:
        picker.load_targets((_TARGET,))
        assert picker.query_one("#known-targets").option_count == 1
        picker.query_one("#manual-target").value = "https://autre.org"
        await pilot.pause()
        assert picker.manual_value == "https://autre.org"


async def test_authorization_checkbox_has_expected_label():
    checkbox = AuthorizationCheckbox()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield checkbox

    app = _ProbeApp()
    async with app.run_test():
        assert "autorise" in str(checkbox.label)
        assert checkbox.value is False


async def test_theme_badge_updates_text():
    badge = ThemeBadge("omega-base")

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield badge

    app = _ProbeApp()
    async with app.run_test():
        badge.update_theme("omega-neon")
        assert badge.visual.plain == "omega-neon"


async def test_render_profile_badge_updates_text():
    badge = RenderProfileBadge(RenderProfile.STANDARD)

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield badge

    app = _ProbeApp()
    async with app.run_test():
        assert badge.visual.plain == "standard"
        badge.update_profile(RenderProfile.MONO)
        assert badge.visual.plain == "mono"


async def test_notification_bar_is_callable_as_a_sink():
    bar = NotificationBar()

    class _ProbeApp(App):
        def compose(self) -> ComposeResult:
            yield bar

    app = _ProbeApp()
    async with app.run_test():
        bar("Debit anormalement bas detecte")
        assert bar.visual.plain == "Debit anormalement bas detecte"
        assert not bar.has_class("-hidden")
        bar.clear_message()
        assert bar.has_class("-hidden")
