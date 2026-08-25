# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""DTO de requete et de resultat d'export."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExportRequestDTO:
    """Requete d'export telle que saisie par l'utilisateur (panneau
    "Sortie" ou commande CLI export)."""

    run_id: str
    format: str
    destination_path: str
    export_theme: str = "omega-base"


@dataclass(frozen=True, slots=True)
class ExportResultDTO:
    """Resultat d'un export reussi."""

    job_id: str
    written_path: str

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - ExportRequestDTO : entree d'application/commands/export_run_report.py
#   (a venir), deja alignee sur ExportJob mais sans id ni created_at
#   (attribues par le command au moment de la creation).
# - ExportResultDTO : sortie du meme command, confirmant l'emplacement
#   ecrit.
# Pourquoi dans application/dto/ (charte) :
# - Objets de transfert : la presentation ne construit jamais un
#   domain/reports/models.py::ExportJob elle-meme.
# Ce qu'il ne contient PAS :
# - Aucun contenu de rapport (voir domain/reports/models.py::ReportContent,
#   qui reste interne a application/infrastructure, jamais expose comme
#   DTO — la presentation ne recoit qu'une confirmation d'ecriture, pas le
#   contenu integral).
# Points cles :
# - export_theme a la meme valeur par defaut ("omega-base") que
#   domain/reports/models.py::ExportJob, pour ne pas introduire un
#   deuxieme defaut divergent.
# Comment il sera utilise (apercu) :
# - application/commands/export_run_report.py (a construire avec le
#   pipeline) recevra un ExportRequestDTO et retournera un
#   Result[ExportResultDTO, DomainError].
#---------------------------------------------------------------------->
