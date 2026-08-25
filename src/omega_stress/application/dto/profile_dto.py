# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""DTO expose a la presentation pour un Profil."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfileDTO:
    """Vue plate d'un Profil, prete pour l'affichage (TUI ou CLI). Aucune
    logique, aucune methode — seulement des champs deja formates en types
    simples (str/bool/float), voir application/dto/mappers.py::profile_to_dto."""

    id: str
    name: str
    description: str
    default_target_id: str
    family: str
    level: str
    duration_minutes: int
    max_error_rate: float
    max_p95_latency_ms: float | None
    tags: tuple[str, ...]
    extended_duration_authorized: bool
    frozen: bool
    favorite: bool
    archived: bool
    created_at: str
    frozen_at: str | None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Forme plate et serialisable d'un Profil, sans reference a des types
#   domaine (Duration, Thresholds, IntensityLevel...).
# Pourquoi dans application/dto/ (charte) :
# - Objet de transfert entre application et presentation : jamais
#   l'entite domain/profiles/models.py::Profile n'est exposee telle
#   quelle a interfaces/.
# Ce qu'il ne contient PAS :
# - Aucune methode, aucune validation : un DTO ne fait que porter des
#   donnees deja validees en amont par le domaine.
# Points cles :
# - family/level restent des chaines (`.value` des enums), pas les enums
#   eux-memes : un DTO ne doit pas forcer la presentation a importer
#   core/enums.py pour un simple affichage.
# - created_at/frozen_at sont deja au format ISO 8601 (str), pas des
#   objets datetime : une presentation CLI/JSON n'a pas a reformater une
#   date.
# Comment il sera utilise (apercu) :
# - application/dto/mappers.py::profile_to_dto() le produit a partir d'un
#   Profile.
# - interfaces/tui/presenters/profile_presenter.py et
#   interfaces/cli/formatters/text_formatter.py le consomment.
#---------------------------------------------------------------------->
