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
    """Echelle d'intensite unique a 8 paliers (Faible/Bas/Moyen-Normal/
    Haut-Fort/Puissant/Agressif/Violent/Maximum), appliquee en palier
    fixe ou en montee progressive selon la famille de test — voir
    omega-stress-calibrage-profils-securite.md. HAUT porte le sens
    "Haut/Fort fusionne" (un seul niveau, pas deux). Ordre de
    declaration = ordre d'iteration croissant, consomme directement par
    les listes deroulantes TUI/CLI (aucun tri supplementaire cote
    interface)."""

    FAIBLE = "faible"
    BAS = "bas"
    MOYEN = "moyen"
    HAUT = "haut"
    PUISSANT = "puissant"
    AGRESSIF = "agressif"
    VIOLENT = "violent"
    MAXIMUM = "maximum"


class DurationPresetId(str, Enum):
    """Identifiant court d'un profil de duree nomme D1-D6 (mode "profil",
    coexiste avec le mode manuel de IntensityLevel/allowed_durations_
    minutes) — voir domain/load/duration_presets.py::DURATION_PRESETS
    pour les valeurs concretes (duree totale, plage de niveaux)."""

    D1 = "d1"
    D2 = "d2"
    D3 = "d3"
    D4 = "d4"
    D5 = "d5"
    D6 = "d6"


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
# - RenderProfile : n'est plus defini ici (migration omega_lib, D-008) —
#   voir omega_lib.terminal.models.RenderProfile, partage par toute la
#   suite (CHECK/DEEP/FOLD/FUZZ), plus une copie locale.
# Points cles :
# - Toutes les enums heritent de str en plus d'Enum : serialisation JSON et
#   comparaison directe avec des chaines sans conversion explicite.
# Comment il sera utilise (apercu) :
# - domain/load/policies.py indexe ses tables par IntensityLevel.
# - core/capability.py utilise CapabilityStatus pour tout objet Capability.
# - domain/reports/models.py utilise ExportFormat pour typer ExportJob.format
#   plutot qu'une chaine libre.
# - DurationPresetId (2026-09-01) : place ici plutot que dans domain/load/
#   duration_presets.py (qui la consomme) pour eviter un cycle d'import —
#   domain/load/models.py::LoadPlan porte un DurationPresetId optionnel,
#   et domain/load/duration_presets.py importe RampStep depuis models.py ;
#   les deux ne peuvent pas s'importer mutuellement.
#---------------------------------------------------------------------->
