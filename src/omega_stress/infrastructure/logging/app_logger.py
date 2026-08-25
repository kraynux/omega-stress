# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Acces au logger applicatif technique deja configure."""
from __future__ import annotations

import logging

from omega_stress.infrastructure.logging.config import LOGGER_NAME


def get_app_logger() -> logging.Logger:
    """Retourne le logger applicatif nomme, configure au prealable par
    config.py::configure_logging(). Un appel avant configuration retourne
    un logger stdlib sans handler (comportement par defaut du module
    logging), pas une erreur."""
    return logging.getLogger(LOGGER_NAME)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Point d'acces unique au logger applicatif, pour eviter que chaque
#   module appelle logging.getLogger(LOGGER_NAME) avec le nom recopie a
#   la main a chaque endroit.
# Pourquoi dans infrastructure/logging/ (charte) :
# - Detail d'infrastructure (module stdlib logging).
# Ce qu'il ne contient PAS :
# - Aucune configuration (voir config.py, seul endroit qui appelle
#   setLevel()/addHandler()).
# Points cles :
# - Ce fichier ne fait AUCUNE verification que configure_logging() a deja
#   ete appelee : logging.getLogger() retourne toujours un objet valide
#   (juste sans handler tant que non configure), coherent avec le
#   comportement standard du module.
# Comment il sera utilise (apercu) :
# - Tout module d'infrastructure/ ou de app/ ayant besoin de journaliser
#   un evenement technique (pas d'audit metier) appelle get_app_logger().
#---------------------------------------------------------------------->
