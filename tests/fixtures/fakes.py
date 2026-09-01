"""Fakes en memoire des ports, reutilisables par les tests de application/.

Pas des mocks : de vraies implementations minimales, en memoire, qui
respectent le contrat des Protocol de ports/ — coherent avec
ARCHITECTURE.md §9 ("tout command/query est testable en injectant de faux
ports, sans base SQLite reelle")."""
from __future__ import annotations

from collections.abc import AsyncIterator, Iterable

from omega_lib.terminal.models import TerminalSignals

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.core.capability import Capability
from omega_stress.domain.load.models import LoadPlan
from omega_stress.domain.profiles.models import Profile
from omega_stress.domain.reports.models import ExportJob
from omega_stress.domain.runs.models import IntervalSample, LoadRun
from omega_stress.domain.targets.models import PinnedTarget, Target


class FakeProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, Profile] = {}

    def save(self, profile: Profile) -> None:
        self._profiles[profile.id] = profile

    def get(self, profile_id: str) -> Profile | None:
        return self._profiles.get(profile_id)

    def list_all(self) -> tuple[Profile, ...]:
        return tuple(self._profiles.values())

    def delete(self, profile_id: str) -> None:
        self._profiles.pop(profile_id, None)


class FakeTargetRepository:
    def __init__(self) -> None:
        self._recent: dict[str, Target] = {}
        self._pinned: dict[str, PinnedTarget] = {}

    def save_recent(self, target: Target) -> None:
        self._recent[target.id] = target

    def save_pinned(self, pinned: PinnedTarget) -> None:
        self._pinned[pinned.target.id] = pinned

    def get(self, target_id: str) -> Target | None:
        if target_id in self._pinned:
            return self._pinned[target_id].target
        return self._recent.get(target_id)

    def get_pinned(self, target_id: str) -> PinnedTarget | None:
        return self._pinned.get(target_id)

    def list_pinned(self) -> tuple[PinnedTarget, ...]:
        return tuple(self._pinned.values())

    def list_recent(self, *, limit: int = 10) -> tuple[Target, ...]:
        return tuple(list(self._recent.values())[:limit])

    def unpin(self, target_id: str) -> None:
        self._pinned.pop(target_id, None)


class FakeRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, LoadRun] = {}

    def save(self, run: LoadRun) -> None:
        self._runs[run.id] = run

    def get(self, run_id: str) -> LoadRun | None:
        return self._runs.get(run_id)

    def list_history(
        self,
        *,
        target_id: str | None = None,
        profile_id: str | None = None,
        limit: int = 50,
    ) -> tuple[LoadRun, ...]:
        runs = list(self._runs.values())
        if target_id is not None:
            runs = [r for r in runs if r.target_id == target_id]
        if profile_id is not None:
            runs = [r for r in runs if r.profile_id == profile_id]
        runs.sort(key=lambda r: r.started_at, reverse=True)
        return tuple(runs[:limit])


class FakeExportRepository:
    def __init__(self) -> None:
        self._jobs: list[ExportJob] = []

    def save(self, job: ExportJob) -> None:
        self._jobs.append(job)

    def list_for_run(self, run_id: str) -> tuple[ExportJob, ...]:
        return tuple(j for j in self._jobs if j.run_id == run_id)


class FakeSettingsStore:
    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self._data: dict[str, str] = dict(initial or {})

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


class FakeTerminalDetector:
    def __init__(self, signals: TerminalSignals) -> None:
        self._signals = signals

    def detect(self) -> TerminalSignals:
        return self._signals


class FakeSystemProbe:
    def __init__(self, capabilities: tuple[Capability, ...] = ()) -> None:
        self._capabilities = capabilities

    def probe(self) -> tuple[Capability, ...]:
        return self._capabilities


class FakeLoadRunner:
    """Rejoue une sequence fixe d'IntervalSample, avec une panne technique
    optionnelle (RunnerFailureError) apres N echantillons."""

    def __init__(
        self,
        samples: Iterable[IntervalSample],
        *,
        raise_after: int | None = None,
    ) -> None:
        self._samples = list(samples)
        self._raise_after = raise_after

    async def run(self, plan: LoadPlan, *, target_url: str) -> AsyncIterator[IntervalSample]:
        for index, sample in enumerate(self._samples):
            if self._raise_after is not None and index == self._raise_after:
                raise RunnerFailureError("panne technique simulee")
            yield sample


class FakeRunProgressNotifier:
    def __init__(self) -> None:
        self.notifications: list[tuple[str, IntervalSample]] = []

    def notify(self, run_id: str, sample: IntervalSample) -> None:
        self.notifications.append((run_id, sample))


class FakeReportExporter:
    def __init__(self, written_path: str = "/tmp/report") -> None:
        self._written_path = written_path
        self.exported: list[tuple[object, ExportJob]] = []

    def export(self, content: object, job: ExportJob) -> str:
        self.exported.append((content, job))
        return self._written_path
