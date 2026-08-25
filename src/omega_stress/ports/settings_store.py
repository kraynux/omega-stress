# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de lecture/ecriture des preferences globales (settings.json)."""
from __future__ import annotations

from typing import Protocol


class SettingsStore(Protocol):
    """Port consomme par application/, implemente par
    infrastructure/storage/files/json_settings_store.py."""

    def get(self, key: str, default: str | None = None) -> str | None: ...

    def set(self, key: str, value: str) -> None: ...

    def all(self) -> dict[str, str]: ...

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Contrat generique cle/valeur pour les preferences globales (theme
#   selectionne, mode auto/manuel, chemin d'export par defaut, flags
#   experimentaux — voir plan produit, "Donnees a stocker en JSON").
# Pourquoi dans ports/ (charte) :
# - Defini par le besoin applicatif (lire/ecrire une preference nommee),
#   jamais par la structure du fichier settings.json (pas de methode
#   "load_json()"/"dump_json()" qui trahirait le format concret).
# Ce qu'il ne contient PAS :
# - Aucune donnee metier (cibles, profils, runs — voir les repositories
#   dedies, backes par SQLite) : ce port ne concerne QUE les preferences
#   globales au sens du plan produit.
# - Aucune implementation (voir
#   infrastructure/storage/files/json_settings_store.py).
# Points cles :
# - Valeurs typees `str` uniquement : un appelant ayant besoin d'un autre
#   type (bool, enum) le serialise/deserialise lui-meme — garde le
#   contrat minimal et evite de dupliquer une logique de (dé)serialisation
#   generique ici.
# - all() sert principalement au debug/diagnostic (ecran Reglages), pas au
#   chemin d'execution normal qui doit toujours passer par get()/set()
#   avec une cle explicite.
# Comment il sera utilise (apercu) :
# - application/commands/select_theme.py, select_render_profile.py.
#---------------------------------------------------------------------->
