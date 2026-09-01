from omega_stress.infrastructure.calibration.fingerprint import compute_fingerprint


def test_fingerprint_reports_plausible_machine_values():
    fingerprint = compute_fingerprint()

    assert fingerprint.logical_cpu_count > 0
    assert fingerprint.python_version
    assert fingerprint.os_name
    assert fingerprint.workers_mode == "asyncio-single-process"
    assert fingerprint.scenario_id == "payload-4k"


def test_fingerprint_is_stable_across_calls():
    first = compute_fingerprint()
    second = compute_fingerprint()

    assert first == second
