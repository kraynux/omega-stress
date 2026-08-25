import logging

from omega_stress.infrastructure.logging.app_logger import get_app_logger
from omega_stress.infrastructure.logging.config import configure_logging


def test_configure_logging_creates_log_file(tmp_path):
    log_path = tmp_path / "app.log"

    configure_logging(log_path=log_path)
    get_app_logger().info("hello")
    for handler in get_app_logger().handlers:
        handler.flush()

    assert log_path.exists()
    assert "hello" in log_path.read_text(encoding="utf-8")


def test_reconfiguring_does_not_duplicate_handlers(tmp_path):
    log_path = tmp_path / "app.log"

    configure_logging(log_path=log_path)
    configure_logging(log_path=log_path)

    assert len(get_app_logger().handlers) == 1


def test_logger_level_is_applied(tmp_path):
    configure_logging(log_path=tmp_path / "app.log", level=logging.WARNING)

    assert get_app_logger().level == logging.WARNING
