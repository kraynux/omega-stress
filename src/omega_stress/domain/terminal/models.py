# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites du sous-domaine terminal : signaux bruts et profil de rendu resolu."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import RenderProfile


@dataclass(frozen=True, slots=True)
class TerminalSignals:
    """Signaux bruts remontes par
    infrastructure/terminal/raw_capabilities.py — aucune decision ici,
    uniquement des faits observes."""

    family: str
    columns: int
    rows: int
    is_ssh: bool = False


@dataclass(frozen=True, slots=True)
class TerminalProfile:
    """Resultat de la decision prise par
    domain/terminal/service.py::resolve_render_profile a partir de
    TerminalSignals."""

    signals: TerminalSignals
    render_profile: RenderProfile

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - TerminalSignals : faits bruts (famille normalisee, taille, SSH ou non).
# - TerminalProfile : decision consolidee (profil de rendu retenu).
# Pourquoi dans domain/terminal/ (charte) :
# - Value objects metier purs ; la distinction signaux/decision reflete la
#   chaine Capacites de ARCHITECTURE.md §4 (detection -> decision), evite
#   de melanger fait observe et interpretation dans un seul objet.
# Ce qu'il ne contient PAS :
# - Aucune lecture d'environnement (os.environ, taille reelle du
#   terminal) : c'est infrastructure/terminal/raw_capabilities.py qui
#   produit un TerminalSignals a partir de ces sources.
# - Aucune logique de decision (voir domain/terminal/service.py).
# Points cles :
# - family est une chaine normalisee (minuscules, tirets), pas un enum :
#   la liste des familles connues n'est pas fermee (voir
#   DEFAULT_RENDER_PROFILE en policies.py pour le cas non reconnu),
#   contrairement a IntensityLevel/TestFamily qui sont des ensembles clos
#   du produit.
# Comment il sera utilise (apercu) :
# - infrastructure/terminal/detector.py construit un TerminalSignals.
# - domain/terminal/service.py le transforme en TerminalProfile.
# - interfaces/tui/rendering/render_profile_resolver.py applique le
#   TerminalProfile.render_profile decide, sans jamais le recalculer.
#---------------------------------------------------------------------->
