from omega_stress.infrastructure.storage.files.json_settings_store import JsonSettingsStore


def test_get_returns_default_when_file_absent(tmp_path):
    store = JsonSettingsStore(tmp_path / "settings.json")

    assert store.get("theme") is None
    assert store.get("theme", "omega-base") == "omega-base"


def test_set_then_get_roundtrips(tmp_path):
    store = JsonSettingsStore(tmp_path / "settings.json")

    store.set("theme", "omega-neon")

    assert store.get("theme") == "omega-neon"


def test_set_persists_across_new_instances(tmp_path):
    path = tmp_path / "settings.json"
    JsonSettingsStore(path).set("theme", "omega-neon")

    reopened = JsonSettingsStore(path)

    assert reopened.get("theme") == "omega-neon"


def test_creates_parent_directory_if_missing(tmp_path):
    path = tmp_path / "nested" / "settings.json"
    store = JsonSettingsStore(path)

    store.set("theme", "omega-base")

    assert path.exists()


def test_all_returns_every_stored_key(tmp_path):
    store = JsonSettingsStore(tmp_path / "settings.json")
    store.set("theme", "omega-base")
    store.set("render_profile", "complete")

    assert store.all() == {"theme": "omega-base", "render_profile": "complete"}
