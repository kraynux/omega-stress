# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation fichier JSON du port SettingsStore."""
from __future__ import annotations

import json
from pathlib import Path

from omega_stress.infrastructure.exceptions import StorageError


class JsonSettingsStore:
    """Implemente ports/settings_store.py::SettingsStore, sur un fichier
    JSON plat (voir plan produit, "settings.json pour preferences
    globales"). Charge tout le fichier en memoire a chaque acces : le
    volume de preferences reste trivial (quelques cles), pas de cache
    ni d'ecriture partielle necessaire en V1."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._read().get(key, default)

    def set(self, key: str, value: str) -> None:
        data = self._read()
        data[key] = value
        self._write(data)

    def all(self) -> dict[str, str]:
        return self._read()

    def _read(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                data: dict[str, str] = json.load(handle)
                return data
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Echec de lecture de {self._path} : {exc}") from exc

    def _write(self, data: dict[str, str]) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
        except OSError as exc:
            raise StorageError(f"Echec d'ecriture de {self._path} : {exc}") from exc

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Implementation concrete du port settings_store.py sur un fichier
#   JSON plat, sans dependance a SQLite (coherent avec le plan produit,
#   qui separe explicitement settings.json de app.db).
# Pourquoi dans infrastructure/storage/files/ (charte) :
# - Adaptateur remplacable, distinct des repositories SQLite : le plan
#   produit separe volontairement preferences globales (JSON) et donnees
#   metier (SQLite), pas la meme techno de stockage.
# Ce qu'il ne contient PAS :
# - Aucun import sqlite3 (contrairement a infrastructure/storage/sqlite/).
# - Aucune ecriture atomique (pas de fichier temporaire + rename) : le
#   volume et la frequence d'ecriture attendus (quelques preferences,
#   usage mono-utilisateur local) ne justifient pas cette robustesse
#   supplementaire en V1 — a reconsiderer si une corruption reelle est
#   observee en usage.
# Points cles :
# - _read()/_write() relisent/reecrivent le fichier entier a chaque
#   appel : plus simple qu'un cache en memoire synchronise, au prix d'un
#   acces disque par operation — largement suffisant pour la frequence
#   d'usage attendue (changement de theme, de profil de rendu...).
# - Fichier absent traite comme un dict vide (jamais une erreur) : un
#   premier lancement sans settings.json prealable reste un cas normal.
# Comment il sera utilise (apercu) :
# - application/commands/select_theme.py, select_render_profile.py.
#---------------------------------------------------------------------->
