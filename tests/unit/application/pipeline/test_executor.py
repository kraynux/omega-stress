from datetime import datetime, timezone

from omega_stress.application.pipeline.executor import execute
from omega_stress.core.enums import IntensityLevel, RunVerdict, TestFamily
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.runs.models import IntervalSample, LoadRun, SystemSnapshot
from tests.fixtures.fakes import FakeLoadRunner, FakeRunProgressNotifier

STARTED = datetime(2026, 8, 24, 10, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 8, 24, 10, 3, tzinfo=timezone.utc)


def _plan(**overrides) -> LoadPlan:
    defaults = dict(
        id="plan-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.5),
        target_authorization_confirmed=True,
    )
    defaults.update(overrides)
    return LoadPlan(**defaults)


def _run() -> LoadRun:
    return LoadRun(
        id="run-1",
        profile_id=None,
        target_id="t-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        started_at=STARTED,
    )


def _sample(**overrides) -> IntervalSample:
    defaults = dict(
        at_second=1.0,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
    )
    defaults.update(overrides)
    return IntervalSample(**defaults)


async def _run_pipeline(plan, run, samples, **kwargs):
    notifier = FakeRunProgressNotifier()
    audit_events = []
    notifications = []

    finished = await execute(
        plan,
        run=run,
        target_url="https://example.org/",
        requested_rate_per_minute=250,
        load_runner=FakeLoadRunner(samples, raise_after=kwargs.get("raise_after")),
        run_progress_notifier=notifier,
        audit_sink=audit_events.append,
        notification_sink=notifications.append,
        now=lambda: NOW,
    )
    return finished, notifier, audit_events, notifications


async def test_clean_run_finishes_with_success():
    finished, notifier, audit_events, notifications = await _run_pipeline(
        _plan(), _run(), [_sample(), _sample()]
    )

    assert finished.result.verdict is RunVerdict.SUCCESS
    assert finished.finished_at == NOW
    assert len(notifier.notifications) == 2
    assert [e.action for e in audit_events] == ["run_started", "run_finished"]
    assert notifications == []


async def test_errors_produce_degraded_verdict():
    finished, *_ = await _run_pipeline(
        _plan(), _run(), [_sample(error_count=1, request_count=10)]
    )

    assert finished.result.verdict is RunVerdict.DEGRADED


async def test_local_bottleneck_produces_degraded_verdict_and_notification():
    finished, _, _, notifications = await _run_pipeline(
        _plan(), _run(), [_sample(observed_rate_per_minute=100.0)]
    )

    assert finished.result.verdict is RunVerdict.DEGRADED
    assert len(notifications) == 1


async def test_threshold_breach_triggers_auto_stop_and_short_circuits():
    plan = _plan(thresholds=Thresholds(max_error_rate=0.1))
    samples = [
        _sample(error_count=8, request_count=10),
        _sample(),  # ne doit jamais etre consomme
    ]

    finished, notifier, audit_events, notifications = await _run_pipeline(plan, _run(), samples)

    assert finished.result.verdict is RunVerdict.AUTO_STOPPED
    assert len(notifier.notifications) == 1  # arrete avant le 2e echantillon
    assert any("Arret automatique" in n for n in notifications)
    assert [e.action for e in audit_events] == ["run_started", "run_finished"]


async def test_sliding_window_breach_stops_a_run_that_per_interval_threshold_alone_would_miss():
    # Chaque intervalle reste sous le seuil PAR INTERVALLE (40% < 50%),
    # mais le volume cumule (20 requetes, minimum atteint au 2e
    # echantillon) fait ressortir un taux d'erreur cumule de 40% >= 30%
    # (policies.WINDOW_TOTAL_ERROR_RATE_ABORT_THRESHOLD) : preuve que
    # check_sliding_window() attrape ce que check_threshold() seul
    # laisserait passer.
    plan = _plan(thresholds=Thresholds(max_error_rate=0.5))
    samples = [
        _sample(at_second=1.0, error_count=4, request_count=10),
        _sample(at_second=2.0, error_count=4, request_count=10),
        _sample(at_second=3.0, error_count=4, request_count=10),  # ne doit jamais etre consomme
    ]

    finished, notifier, audit_events, notifications = await _run_pipeline(plan, _run(), samples)

    assert finished.result.verdict is RunVerdict.AUTO_STOPPED
    assert len(notifier.notifications) == 2  # arret des que le volume minimum est atteint
    assert finished.result.events[0].kind == "window_error_rate_exceeded"
    assert any("fenetre" in n for n in notifications)


async def test_runner_failure_produces_failed_verdict():
    finished, notifier, audit_events, _ = await _run_pipeline(
        _plan(), _run(), [_sample(), _sample()], raise_after=1
    )

    assert finished.result.verdict is RunVerdict.FAILED
    assert len(notifier.notifications) == 1  # le premier echantillon a ete traite avant la panne


async def test_runner_failure_records_the_exception_message_as_an_event():
    finished, *_ = await _run_pipeline(
        _plan(), _run(), [_sample(), _sample()], raise_after=1
    )

    assert finished.result is not None
    assert len(finished.result.events) == 1
    event = finished.result.events[0]
    assert event.kind == "runner_failure"
    assert event.message == "panne technique simulee"
    assert event.occurred_at == NOW


async def test_threshold_breach_auto_stop_records_the_reason_as_an_event():
    plan = _plan(thresholds=Thresholds(max_error_rate=0.1))
    samples = [_sample(error_count=8, request_count=10)]

    finished, *_ = await _run_pipeline(plan, _run(), samples)

    assert finished.result is not None
    assert len(finished.result.events) == 1
    assert finished.result.events[0].kind == "threshold_exceeded"


async def test_generator_cpu_breach_triggers_auto_stop_when_safety_mode_enabled():
    # Bug reel corrige le 2026-09-01 ("mode securite" a cocher) :
    # safety_mode=True (defaut) preserve le comportement existant.
    plan = _plan(safety_mode=True)
    hot = SystemSnapshot(cpu_percent_generator=99.0, cpu_percent_global=95.0)
    samples = [_sample(at_second=float(i), system=hot) for i in range(1, 4)] + [
        _sample(at_second=4.0)  # ne doit jamais etre consomme
    ]

    finished, notifier, *_ = await _run_pipeline(plan, _run(), samples)

    assert finished.result.verdict is RunVerdict.AUTO_STOPPED
    assert finished.result.events[0].kind == "generator_cpu_exceeded"
    assert len(notifier.notifications) == 3


async def test_generator_cpu_breach_does_not_stop_when_safety_mode_disabled():
    # check_generator_resources() n'est meme plus evalue : threshold_
    # guard/check_sliding_window (protection de la CIBLE) restent actifs,
    # inchanges.
    plan = _plan(safety_mode=False)
    hot = SystemSnapshot(cpu_percent_generator=99.0, cpu_percent_global=95.0)
    samples = [_sample(at_second=float(i), system=hot) for i in range(1, 4)]

    finished, notifier, *_ = await _run_pipeline(plan, _run(), samples)

    assert finished.result.verdict is RunVerdict.SUCCESS
    assert len(notifier.notifications) == 3
