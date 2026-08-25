import json
from datetime import datetime, timezone

from omega_stress.core.audit import AuditEvent
from omega_stress.infrastructure.logging.audit_logger import AuditLogger

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def test_record_appends_one_json_line_per_event(tmp_path):
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path)

    logger.record(AuditEvent(action="run_started", outcome="ok", authorized=True, occurred_at=NOW))
    logger.record(
        AuditEvent(action="run_finished", outcome="success", authorized=True, occurred_at=NOW)
    )

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["action"] == "run_started"
    assert first["authorized"] is True


def test_record_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "audit.jsonl"
    logger = AuditLogger(path)

    logger.record(AuditEvent(action="a", outcome="b", authorized=False, occurred_at=NOW))

    assert path.exists()
