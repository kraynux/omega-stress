import urllib.error
import urllib.request

from omega_stress.domain.calibration.policies import (
    CALIBRATION_PAYLOAD_SIZE_BYTES,
    CALIBRATION_TARGET_PATH,
)
from omega_stress.infrastructure.calibration.local_server import CalibrationLocalServer


def test_server_returns_fixed_payload_on_calibration_path():
    with CalibrationLocalServer() as server, urllib.request.urlopen(
        f"{server.base_url}{CALIBRATION_TARGET_PATH}"
    ) as response:
        body = response.read()

    assert len(body) == CALIBRATION_PAYLOAD_SIZE_BYTES


def test_server_returns_404_on_other_paths():
    with CalibrationLocalServer() as server:
        try:
            urllib.request.urlopen(f"{server.base_url}/autre-chemin")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:
            raise AssertionError("Une reponse 404 etait attendue.")


def test_server_uses_an_ephemeral_port():
    with CalibrationLocalServer() as first, CalibrationLocalServer() as second:
        assert first.base_url != second.base_url
