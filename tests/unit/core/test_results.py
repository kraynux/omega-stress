from omega_stress.core.results import Err, Ok


def test_ok_carries_value_and_flags():
    result = Ok(42)
    assert result.value == 42
    assert result.is_ok is True
    assert result.is_err is False


def test_err_carries_error_and_flags():
    result = Err("boom")
    assert result.error == "boom"
    assert result.is_ok is False
    assert result.is_err is True


def test_ok_and_err_are_distinct_types():
    assert isinstance(Ok(1), Ok)
    assert not isinstance(Ok(1), Err)
    assert isinstance(Err("x"), Err)
    assert not isinstance(Err("x"), Ok)
