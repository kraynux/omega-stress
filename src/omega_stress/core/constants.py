# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Constantes transverses non metier."""
from __future__ import annotations

APP_NAME: str = "omega-stress"
"""Nom produit, utilise pour l'affichage et les chemins par defaut."""

DEFAULT_EXPORT_DIRNAME: str = "exports"
"""Nom du sous-dossier d'export par defaut sous var/ (infrastructure/config/paths.py)."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Regroupe les constantes veritablement transverses et non metier
#   (nom produit, nom de dossier par defaut) utiles a plusieurs couches.
# Pourquoi dans core/ (charte) :
# - Distinct de domain/*/policies.py : aucune de ces constantes n'encode une
#   regle de securite ou de produit (intensite, duree, seuil). Une valeur
#   qui figure dans un tableau du plan produit (plan_omega-stress_v5.md) va
#   dans le policies.py du sous-domaine concerne, jamais ici.
# Ce qu'il ne contient PAS :
# - Aucune table de bornage (voir domain/load/policies.py).
# - Aucun chemin absolu concret (c'est infrastructure/config/paths.py qui
#   les resout a partir de ces noms).
# Points cles :
# - Fichier volontairement tres court : n'y ajouter une constante que si
#   elle est reellement utilisee par au moins deux couches differentes.
# Comment il sera utilise (apercu) :
# - infrastructure/config/paths.py compose var/<DEFAULT_EXPORT_DIRNAME>/.
# - interfaces/cli/main.py affiche APP_NAME.
#---------------------------------------------------------------------->
