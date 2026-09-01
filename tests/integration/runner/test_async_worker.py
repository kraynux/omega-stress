import httpx

from omega_stress.infrastructure.runner.async_worker import perform_request


async def test_successful_response_is_marked_success():
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.success is True
    assert outcome.latency_ms >= 0.0
    assert outcome.error_category is None


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


async def test_5xx_status_is_categorized_http_5xx():
    transport = httpx.MockTransport(lambda request: httpx.Response(503))
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.error_category == "http_5xx"


async def test_4xx_status_is_categorized_http_4xx():
    transport = httpx.MockTransport(lambda request: httpx.Response(404))
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.error_category == "http_4xx"


async def test_connection_error_is_categorized_connection():
    def _raise(request):
        raise httpx.ConnectError("refused", request=request)

    transport = httpx.MockTransport(_raise)
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.error_category == "connection"


async def test_timeout_is_categorized_timeout_not_connection():
    def _raise(request):
        raise httpx.ConnectTimeout("timed out", request=request)

    transport = httpx.MockTransport(_raise)
    async with httpx.AsyncClient(transport=transport) as client:
        outcome = await perform_request(client, "https://example.org/")

    assert outcome.error_category == "timeout"
