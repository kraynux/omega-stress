from __future__ import annotations

import pytest

from omega_stress.infrastructure.storage.sqlite.connection import open_connection
from omega_stress.infrastructure.storage.sqlite.migrations import apply_schema


@pytest.fixture
def sqlite_connection(tmp_path):
    """Connexion SQLite isolee (fichier temporaire), schema deja applique
    — reutilisee par tous les tests d'integration de infrastructure/storage/sqlite/."""
    connection = open_connection(tmp_path / "test.db")
    apply_schema(connection)
    yield connection
    connection.close()
