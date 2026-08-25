# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Resolution des chemins runtime (var/), la seule source de verite pour ces chemins."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VAR_DIRNAME = "var"
ENV_VAR_DIR = "OMEGA_STRESS_VAR_DIR"


def resolve_var_dir() -> Path:
    """Racine des fichiers runtime : `$OMEGA_STRESS_VAR_DIR` si defini,
    sinon `./var` relatif au repertoire courant d'execution."""
    override = os.environ.get(ENV_VAR_DIR)
    if override:
        return Path(override)
    return Path.cwd() / DEFAULT_VAR_DIRNAME


def db_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "db" / "app.db"


def settings_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "settings.json"


def exports_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "exports"


def screenshots_dir(var_dir: Path | None = None) -> Path:
    """Dossier de destination par defaut des captures d'ecran SVG (voir
    interfaces/tui/app.py, commande "Capture d'ecran" de la palette) —
    bug reel rapporte (2026-08-25) : sans ce chemin, Textual sauvegardait
    les captures dans le repertoire de TELECHARGEMENTS de l'utilisateur
    (comportement par defaut de App.deliver_screenshot() quand aucun
    `path=` n'est fourni), jamais dans var/ comme les exports."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "screenshots"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seule source de verite pour les chemins runtime (base SQLite,
#   settings.json, dossier d'export par defaut, dossier de captures
#   d'ecran par defaut).
# Pourquoi dans infrastructure/config/ (charte) :
# - Chemins concrets sur le systeme de fichiers : un detail
#   d'infrastructure, jamais une politique de domaine.
# Ce qu'il ne contient PAS :
# - Aucune creation de fichier/dossier (voir infrastructure/storage/
#   sqlite/connection.py et json_settings_store.py, qui creent les
#   dossiers parents au besoin ; interfaces/tui/app.py fait de meme avant
#   de livrer une capture d'ecran, voir son propre INFO DEV).
# Points cles :
# - Chaque fonction accepte un `var_dir` optionnel : permet aux tests
#   d'infrastructure d'injecter un `tmp_path` isole, sans dependre de
#   variables d'environnement ni du repertoire courant reel.
# - screenshots_dir() (2026-08-25) : meme patron que exports_dir(), pour
#   le meme besoin cote utilisateur (bug reel rapporte : "chemin des
#   screenshots en svg a modifier dans var/screenshots/" — les captures
#   partaient jusqu'ici dans le dossier Telechargements par defaut de
#   Textual, jamais dans var/, voir sa propre docstring).
# - resolve_var_dir() reste relatif a Path.cwd() par defaut (coherent
#   avec l'usage local mono-utilisateur du produit) plutot qu'un
#   repertoire XDG/utilisateur — a revoir si une distribution multi-
#   utilisateur est envisagee plus tard.
# Comment il sera utilise (apercu) :
# - app/bootstrap.py appelle resolve_var_dir() une fois au demarrage et
#   propage les chemins concrets aux adaptateurs construits.
# - Chaque test d'integration de infrastructure/storage/ passe un
#   var_dir=tmp_path explicite.
#---------------------------------------------------------------------->
