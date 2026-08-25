import httpx

from omega_stress.infrastructure.runner.async_worker import perform_request


async def test_successful_response_is_marked_success():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.success is True
    assert outcome.latency_ms >= 0.0


async def test_error_status_is_marked_failure():
    transport = httpx.MockTransport(lambda request: httpx.Response(500))
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.success is False


async def test_connection_error_is_absorbed_as_failure():
    def _raise(request):
        raise httpx.ConnectError("refused", request=request)

    transport = httpx.MockTransport(_raise)
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.success is False
