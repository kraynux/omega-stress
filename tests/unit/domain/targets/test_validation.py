from omega_stress.core.results import Err, Ok
from omega_stress.domain.targets.validation import parse_target_address


def test_parses_full_url():
    result = parse_target_address("https://example.org:8443/api/health")

    assert isinstance(result, Ok)
    address = result.value
    assert address.scheme == "https"
    assert address.host == "example.org"
    assert address.port == 8443
    assert address.path == "/api/health"


def test_defaults_to_http_without_scheme():
    result = parse_target_address("example.org")

    assert isinstance(result, Ok)
    assert result.value.scheme == "http"
    assert result.value.host == "example.org"


def test_rejects_empty_input():
    result = parse_target_address("   ")

    assert isinstance(result, Err)


def test_rejects_unsupported_scheme():
    result = parse_target_address("ftp://example.org")

    assert isinstance(result, Err)


def test_rejects_missing_host():
    result = parse_target_address("http://")

    assert isinstance(result, Err)
