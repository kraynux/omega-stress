# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Chargement dynamique des chemins de feuille de style selon le profil de rendu."""
from __future__ import annotations

from omega_lib.terminal.models import RenderProfile

from omega_stress.interfaces.tui.rendering.render_profile_resolver import stylesheet_paths_for


def load_paths_for(profile: RenderProfile) -> list[str]:
    """Retourne les chemins (str, format attendu par
    `textual.app.App.CSS_PATH`) a appliquer pour un profil de rendu
    donne : base.tcss puis le fichier specifique au profil, dans cet
    ordre (Textual applique les feuilles dans l'ordre de la liste,
    dernier gagnant en cas de conflit de specificite egale)."""
    return [str(path) for path in stylesheet_paths_for(profile)]

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Adapte la sortie de render_profile_resolver.py (tuple de Path) au
#   format attendu par `App.CSS_PATH` (liste de chaines), au point
#   d'entree effectif de chargement Textual.
# Pourquoi dans interfaces/tui/rendering/ (charte) :
# - Detail de cablage Textual (le resultat est passe a
#   `super().__init__(css_path=...)`, voir interfaces/tui/app.py), distinct
#   de la DECISION du profil (render_profile_resolver.py) — fichier separe
#   pour ne pas melanger les deux responsabilites (ARCHITECTURE.md §2.4).
# Ce qu'il ne contient PAS :
# - Aucune decision de profil (deja faite en amont).
# - Aucune verification d'existence des fichiers : si base.tcss ou le
#   fichier de profil est absent, Textual leve sa propre erreur au
#   demarrage — pas de garde redondante ici.
# Points cles :
# - Fonction intentionnellement mince : conversion de type uniquement.
# Comment il sera utilise (apercu) :
# - interfaces/tui/app.py::__init__() appelle
#   `super().__init__(css_path=load_paths_for(profile))`.
#---------------------------------------------------------------------->
