# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Resolution d'un nom de theme d'export vers sa palette. Aucun import Jinja2 ici."""
from __future__ import annotations

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES, Palette


def resolve_export_palette(theme_name: str) -> Palette:
    """Lookup pur dans le catalogue de domain/theme/policies.py. Un nom
    inconnu se replie silencieusement sur DEFAULT_EXPORT_THEME — la
    validation d'un nom de theme invalide a deja eu lieu en amont
    (domain/reports/service.py::validate_export_job), ce lookup ne
    revalide jamais rien."""
    return EXPORT_PALETTES.get(theme_name, EXPORT_PALETTES[DEFAULT_EXPORT_THEME])

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul point de traduction nom de theme d'export -> Palette concrete.
# Pourquoi dans infrastructure/exporters/ (charte) :
# - Lookup pur dans une politique de domaine deja figee
#   (domain/theme/policies.py::EXPORT_PALETTES) : aucune logique propre,
#   aucun import Jinja2 (ARCHITECTURE.md §2, precision explicite).
# Ce qu'il ne contient PAS :
# - Aucun import jinja2 (voir html_exporter.py, seul fichier autorise).
# - Aucune validation (deja faite par domain/reports/service.py avant
#   qu'un ExportJob n'atteigne ce fichier).
# Points cles :
# - Repli silencieux sur DEFAULT_EXPORT_THEME pour un nom inconnu : ne
#   devrait normalement jamais arriver (validate_export_job() l'aurait
#   deja rejete), garde-fou de derniere ligne plutot qu'un chemin normal.
# Comment il sera utilise (apercu) :
# - infrastructure/exporters/html_exporter.py.
#---------------------------------------------------------------------->
