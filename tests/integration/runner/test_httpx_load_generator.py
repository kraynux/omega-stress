import httpx
import pytest

from omega_stress.application.exceptions import RunnerFailureError
from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.infrastructure.runner.httpx_load_generator import HttpxLoadGenerator


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
    generator = HttpxLoadGenerator(transport=transport, sleep=_no_sleep)

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    assert len(samples) == 60


async def test_samples_reflect_request_volume_at_bas_level():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(transport=transport, sleep=_no_sleep)

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    # Bas = 250 req/min = ~4.17 req/s, arrondi a 4 par intervalle.
    assert all(sample.request_count == 4 for sample in samples)


async def test_error_responses_are_reflected_in_error_count():
    transport = httpx.MockTransport(lambda request: httpx.Response(500))
    generator = HttpxLoadGenerator(transport=transport, sleep=_no_sleep)

    samples = [
        sample
        async for sample in generator.run(_plan(duration=Duration(minutes=1)), target_url="https://x/")
    ]

    assert all(sample.error_count == sample.request_count for sample in samples)


async def test_unreachable_target_raises_runner_failure_error():
    def _raise(request):
        raise httpx.ConnectError("refused", request=request)

    transport = httpx.MockTransport(_raise)
    generator = HttpxLoadGenerator(transport=transport, sleep=_no_sleep)

    with pytest.raises(RunnerFailureError):
        async for _sample in generator.run(_plan(), target_url="https://x/"):
            pass


async def test_connection_family_uses_concurrency_not_rate():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    generator = HttpxLoadGenerator(transport=transport, sleep=_no_sleep)
    plan = _plan(family=TestFamily.CONNECTION, duration=Duration(minutes=1))

    samples = [sample async for sample in generator.run(plan, target_url="https://x/")]

    # Bas = 25 connexions simultanees.
    assert all(sample.request_count == 25 for sample in samples)
