import asyncio

import httpx
import pytest

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.policies import GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL
from omega_stress.domain.runs.models import SystemSnapshot
from omega_stress.infrastructure.runner.httpx_load_generator import HttpxLoadGenerator


class _FakeSystemSampler:
    """Evite tout appel psutil reel dans ces tests (vitesse, determinisme)
    — voir ports/system_sampler.py::SystemSampler."""

    def __init__(self, snapshot: SystemSnapshot | None = None) -> None:
        self._snapshot = snapshot or SystemSnapshot(cpu_percent_generator=12.5, memory_rss_mb=64.0)

    def sample(self) -> SystemSnapshot:
        return self._snapshot


async def _no_sleep(_seconds: float) -> None:
    """Remplace asyncio.sleep dans les tests : exerce toute la logique de
    pacing sans attendre le temps reel, pour que des plans de plusieurs
    minutes s'executent quasi instantanement."""


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


async def test_produces_one_sample_per_second_of_duration():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    assert len(samples) == 60


async def test_samples_reflect_request_volume_at_bas_level():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    # Bas = 500 req/min = ~8.33 req/s, arrondi a 8 par intervalle.
    assert all(sample.request_count == 8 for sample in samples)


async def test_error_responses_are_reflected_in_error_count():
    transport = httpx.MockTransport(lambda request: httpx.Response(500))
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    assert all(sample.error_count == sample.request_count for sample in samples)


async def test_unreachable_target_raises_runner_failure_error():
    def _raise(request):
        raise httpx.ConnectError("refused", request=request)

    transport = httpx.MockTransport(_raise)
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )

    with pytest.raises(RunnerFailureError):
        async for _sample in generator.run(_plan(), target_url="https://x/"):
            pass


async def test_connection_family_uses_concurrency_not_rate():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )
    plan = _plan(family=TestFamily.CONNECTION, duration=Duration(minutes=1))

    samples = [sample async for sample in generator.run(plan, target_url="https://x/")]

    # Bas = 50 connexions simultanees.
    assert all(sample.request_count == 50 for sample in samples)


async def test_request_family_samples_carry_requested_rate_and_no_connections():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )
    plan = _plan(family=TestFamily.REQUEST, duration=Duration(minutes=1))

    samples = [sample async for sample in generator.run(plan, target_url="https://x/")]

    # Bas = 500 req/min.
    assert all(sample.requested_rate_per_minute == pytest.approx(500.0) for sample in samples)
    assert all(sample.active_connections == 0 for sample in samples)


async def test_connection_family_samples_carry_active_connections_and_no_rate():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )
    plan = _plan(family=TestFamily.CONNECTION, duration=Duration(minutes=1))

    samples = [sample async for sample in generator.run(plan, target_url="https://x/")]

    assert all(sample.requested_rate_per_minute is None for sample in samples)
    assert all(sample.active_connections == 50 for sample in samples)


async def test_run_interval_bounds_concurrent_requests_in_flight():
    # Bug reel rapporte (2026-09-01, captures d'ecran) : Test connexions
    # Agressif/Maximum lancait toutes ses requetes cibles d'un bloc, sans
    # aucune limite de concurrence reelle — voir domain/load/policies.py::
    # GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL pour le diagnostic
    # complet.
    in_flight = 0
    peak = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.001)
        in_flight -= 1
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler()
    )
    plan = _plan(
        family=TestFamily.CONNECTION, level=IntensityLevel.MAXIMUM, duration=Duration(minutes=1)
    )

    stream = generator.run(plan, target_url="https://x/")
    first_sample = await stream.__anext__()
    await stream.aclose()

    # Maximum = 5000 connexions simultanees visees, bien au-dela du
    # plafond technique : confirme que ce test exerce reellement le cas
    # ou throttling doit intervenir.
    assert first_sample.request_count > GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL
    assert peak <= GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL


async def test_samples_carry_the_injected_system_sampler_snapshot():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    snapshot = SystemSnapshot(cpu_percent_generator=42.0, memory_rss_mb=128.0)
    generator = HttpxLoadGenerator(
        transport=transport, sleep=_no_sleep, system_sampler=_FakeSystemSampler(snapshot)
    )

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    assert all(sample.system == snapshot for sample in samples)
