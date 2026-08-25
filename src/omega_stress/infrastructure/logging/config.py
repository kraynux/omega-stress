# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Configuration du logger applicatif technique (stdlib logging)."""
from __future__ import annotations

import logging
from pathlib import Path

LOGGER_NAME = "omega_stress"
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(*, log_path: Path, level: int = logging.INFO) -> logging.Logger:
    """Configure et retourne le logger applicatif nomme `omega_stress`,
    avec un handler fichier unique. Idempotent : rappeler cette fonction
    remplace le handler existant plutot que d'en accumuler."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
    return logger

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'entree unique de configuration du logger applicatif
#   technique (bugs, avertissements internes — pas l'audit metier, voir
#   audit_logger.py, un canal separe et volontairement distinct).
# Pourquoi dans infrastructure/logging/ (charte) :
# - Utilise le module stdlib `logging`, un detail d'infrastructure.
# Ce qu'il ne contient PAS :
# - Aucune ecriture d'evenement d'audit structure (voir audit_logger.py).
# - Aucun appel a logging.basicConfig() global : ce projet configure un
#   logger nomme dedie, pour ne pas interferer avec la configuration de
#   logging d'un eventuel appelant exterieur (tests, embarque dans un
#   autre outil).
# Points cles :
# - logger.propagate = False : evite une double emission si le logger
#   racine Python est configure ailleurs (ex. par pytest).
# - handlers.clear() avant d'ajouter le nouveau : rend configure_logging()
#   surete a rappeler plusieurs fois (ex. tests), sans accumuler de
#   handlers dupliques qui dupliqueraient chaque ligne de log.
# Comment il sera utilise (apercu) :
# - app/bootstrap.py appelle configure_logging() une fois au demarrage.
# - infrastructure/logging/app_logger.py::get_app_logger() recupere
#   ensuite ce meme logger par son nom, sans le reconfigurer.
#---------------------------------------------------------------------->
