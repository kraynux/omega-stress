import pytest

from omega_stress.domain.targets.models import TargetAddress


def test_base_url_without_port():
    address = TargetAddress(scheme="https", host="example.org", path="/api")
    assert address.base_url == "https://example.org/api"


def test_base_url_with_port():
    address = TargetAddress(scheme="http", host="localhost", port=8080, path="/")
    assert address.base_url == "http://localhost:8080/"


def test_rejects_unsupported_scheme():
    with pytest.raises(ValueError):
        TargetAddress(scheme="ftp", host="example.org")


def test_rejects_empty_host():
    with pytest.raises(ValueError):
        TargetAddress(scheme="http", host="")
