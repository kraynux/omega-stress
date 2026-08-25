# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Enumerations transverses partagees par plusieurs couches."""
from __future__ import annotations

from enum import Enum


class TestFamily(str, Enum):
    """Les trois familles de test du produit (vocabulaire normatif, voir
    plan_omega-stress_v5.md, section Positionnement terminologique)."""

    REQUEST = "request"
    CONNECTION = "connection"
    RAMP = "ramp"


class IntensityLevel(str, Enum):
    """Echelle d'intensite unique (Bas/Moyen/Haut/Maximum), appliquee en
    palier fixe ou en montee progressive selon la famille de test."""

    BAS = "bas"
    MOYEN = "moyen"
    HAUT = "haut"
    MAXIMUM = "maximum"


class RenderProfile(str, Enum):
    """Niveau de complexite structurelle affiche par le TUI, decide depuis
    la capacite terminal detectee (distinct du choix de theme de couleur)."""

    COMPLETE = "complete"
    STANDARD = "standard"
    REDUCED = "reduced"
    MONO = "mono"


class RunVerdict(str, Enum):
    """Issue finale d'un run, construite a partir des DomainError plutot que
    d'un message d'exception libre."""

    SUCCESS = "success"
    DEGRADED = "degraded"
    AUTO_STOPPED = "auto_stopped"
    FAILED = "failed"


class CapabilityStatus(str, Enum):
    """Statut d'une capacite consolidee dans core/capability_registry.py."""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    MISSING = "missing"
    DISQUALIFIED = "disqualified"


class ExportFormat(str, Enum):
    """Formats d'export d'un run (voir plan produit, "Export detaille") :
    JSON pour donnees brutes et reimport, CSV pour analyse tabulaire, HTML
    pour rapport lisible."""

    JSON = "json"
    CSV = "csv"
    HTML = "html"

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Regroupe les enumerations utilisees par plusieurs couches (domain,
#   application, infrastructure, interfaces) pour eviter que chacune ne
#   redefinisse sa propre version legerement divergente.
# Pourquoi dans core/ (charte) :
# - Vocabulaire transverse au sens strict : ni une regle metier (les VALEURS
#   associees a chaque niveau vivent en domain/load/presets.py, pas ici),
#   ni un detail technique.
# Ce qu'il ne contient PAS :
# - Aucune table de valeurs numeriques (durees, seuils, req/min) : ce sont
#   des politiques de domaine, voir domain/load/policies.py et presets.py.
# - Aucune logique de decision (quel profil pour quel terminal, etc.) : ce
#   sont des services de domain/terminal/service.py.
# Points cles :
# - Toutes les enums heritent de str en plus d'Enum : serialisation JSON et
#   comparaison directe avec des chaines sans conversion explicite.
# - RenderProfile != le theme "omega-mono" du catalogue de theme (voir
#   ARCHITECTURE.md §8 et Projet/themes.txt) : piege de nommage documente
#   pour ne pas etre reintroduit ici.
# Comment il sera utilise (apercu) :
# - domain/load/policies.py indexe ses tables par IntensityLevel.
# - domain/terminal/service.py et domain/terminal/policies.py produisent un
#   RenderProfile ; interfaces/tui/rendering/render_profile_resolver.py le
#   consomme sans jamais le recalculer.
# - core/capability.py utilise CapabilityStatus pour tout objet Capability.
# - domain/reports/models.py utilise ExportFormat pour typer ExportJob.format
#   plutot qu'une chaine libre.
#---------------------------------------------------------------------->
