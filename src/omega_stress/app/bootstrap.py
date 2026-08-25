# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'assemblage complet de l'application, appele une fois par processus."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from omega_stress.app.dependency_container import DependencyContainer, build_container
from omega_stress.app.lifecycle import AppLifecycle
from omega_stress.infrastructure.config import paths
from omega_stress.infrastructure.logging.config import configure_logging


@dataclass(frozen=True, slots=True)
class Application:
    """Resultat complet du demarrage : le conteneur cable et son cycle
    de vie, prets a etre distribues a interfaces/tui/ ou interfaces/cli/."""

    container: DependencyContainer
    lifecycle: AppLifecycle


def bootstrap(*, var_dir: Path | None = None) -> Application:
    """Sequence de demarrage complete : resout les chemins runtime,
    configure la journalisation technique, cable les adaptateurs
    concrets. Appeler une seule fois par processus (voir
    interfaces/cli/main.py et interfaces/tui/app.py, seuls points
    d'entree qui l'appellent)."""
    base = var_dir if var_dir is not None else paths.resolve_var_dir()

    configure_logging(log_path=base / "app.log")
    container = build_container(var_dir=base)

    return Application(container=container, lifecycle=AppLifecycle(container=container))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Sequence complete de demarrage, dans l'ordre : resolution des
#   chemins, configuration du logger, cablage des adaptateurs.
# Pourquoi dans app/ (charte) :
# - "bootstrap... assembler et demarrer l'application. Jamais de logique
#   metier" : orchestre config.py et dependency_container.py, ne decide
#   rien du metier.
# Ce qu'il ne contient PAS :
# - Aucune logique de commande/query (interfaces/ les appelle directement
#   via les ports exposes par Application.container, jamais via ce
#   fichier).
# - Aucune gestion d'exception applicative : une ConfigurationError levee
#   pendant le demarrage (chemin invalide, permissions insuffisantes)
#   remonte brute jusqu'a l'appelant (interfaces/cli/main.py ou
#   interfaces/tui/app.py), qui decide comment l'afficher — ce fichier ne
#   catche rien lui-meme.
# Points cles :
# - var_dir optionnel : permet aux tests d'isoler completement une
#   application demarree (tmp_path), sans toucher au systeme reel.
# - L'ordre (logging avant cablage) est deliberement fixe : toute erreur
#   pendant build_container() (ex. base SQLite corrompue) peut ainsi deja
#   etre journalisee.
# Comment il sera utilise (apercu) :
# - interfaces/cli/main.py : `app = bootstrap(); ... finally:
#   app.lifecycle.shutdown()`.
# - interfaces/tui/app.py : meme sequence, au demarrage de l'App Textual.
#---------------------------------------------------------------------->
