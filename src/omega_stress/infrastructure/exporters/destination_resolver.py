# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Resolution du fichier final d'un export depuis ExportJob.destination_path."""
from __future__ import annotations

from pathlib import Path

from omega_stress.core.enums import TestFamily
from omega_stress.domain.reports.models import ExportJob, ReportSummary

_FAMILY_SLUGS: dict[TestFamily, str] = {
    TestFamily.REQUEST: "test-requetes",
    TestFamily.CONNECTION: "test-connexions",
    TestFamily.RAMP: "test-charge",
}


def resolve_destination_file(job: ExportJob, summary: ReportSummary, *, extension: str) -> Path:
    """Si `destination_path` designe un dossier (deja existant, ou une
    chaine terminee par un separateur de chemin), y derive un nom de
    fichier lisible `<famille>-<horodatage>.<extension>` (ex.
    `test-requetes-20260824-143207.json`) ; sinon le traite tel quel comme
    un chemin de fichier complet deja fourni par l'appelant."""
    raw = Path(job.destination_path)
    looks_like_a_folder = raw.is_dir() or job.destination_path.endswith(("/", "\\"))
    if looks_like_a_folder:
        slug = _FAMILY_SLUGS[summary.family]
        timestamp = summary.started_at.strftime("%Y%m%d-%H%M%S")
        return raw / f"{slug}-{timestamp}.{extension}"
    return raw

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul endroit du projet qui decide si ExportJob.destination_path
#   designe un DOSSIER (dans lequel deriver un nom de fichier) ou un
#   CHEMIN DE FICHIER COMPLET deja fourni tel quel — partage par les
#   trois exporters concrets pour ne pas tripler la meme regle.
# Pourquoi dans infrastructure/exporters/ (charte) :
# - Verifie l'existence du chemin sur le disque (Path.is_dir(), un acte
#   d'I/O) : ne peut pas vivre en domain/, qui reste sans I/O ; les trois
#   exporters font deja de l'I/O direct (mkdir/write) sans passer par un
#   port dedie pour ce niveau de detail, coherent avec l'existant.
# Ce qu'il ne contient PAS :
# - Aucune ecriture de fichier (deleguee a chaque exporter concret, qui
#   appelle cette fonction puis ecrit lui-meme).
# Points cles :
# - Corrige un bug reel (2026-08-24) : screens/export_dialog.py invite
#   l'utilisateur a saisir un "Dossier de destination", mais les trois
#   exporters traitaient jusque-la `job.destination_path` comme un CHEMIN
#   DE FICHIER complet (`Path(job.destination_path).write_text(...)`
#   direct) — saisir un dossier existant (ex. `var/exports`, exactement
#   ce que le placeholder du champ suggere) levait un `IsADirectoryError`
#   (`OSError` errno 21), traduit en `StorageError` puis JAMAIS rattrape
#   nulle part avant `interfaces/tui/app.py`, qui a son tour ne rattrapait
#   rien avant ce meme jour (voir son propre INFO DEV,
#   `_handle_exception()`) — les deux bugs se cumulaient pour fermer toute
#   l'application sur un export HTML vers un dossier.
# - Le detecteur "termine par un separateur" (avant meme de toucher le
#   disque) couvre le cas d'un dossier PAS ENCORE cree (ex. utilisateur
#   saisit `var/exports/` pour un run tout juste ajoute) : `Path.is_dir()`
#   seul aurait manque ce cas, forcant l'utilisateur a creer le dossier a
#   la main avant de pouvoir exporter dedans.
# - Un chemin de fichier explicite (ex. `--destination rapport.json` en
#   CLI, ou `var/exports/mon-rapport.html` dans le TUI) reste traite tel
#   quel : ce module ne force jamais une convention de nommage a un
#   appelant qui a deja choisi un nom de fichier precis.
# - Nom de fichier lisible (2026-08-24, remplace `<run_id>.<extension>`) :
#   un run_id est un identifiant opaque (shared/ids.py::new_id()), illisible
#   tel quel dans un gestionnaire de fichiers — bug reel rapporte ("les
#   noms des exports sont illisibles"). `<famille>-<horodatage>` reprend
#   le format demande explicitement (ex. "test-charge-date"). Aucune
#   garantie d'unicite au-dela de la seconde (summary.started_at n'a pas
#   de suffixe desambiguisant) : deux exports du meme run vers le meme
#   dossier a la meme seconde s'ecrasent l'un l'autre — accepte
#   deliberement, un nom lisible etait le point explicite de ce
#   correctif, pas l'unicite garantie (deja hors de portee avec
#   `<run_id>.<extension>` de toute facon : reexporter le MEME run vers le
#   MEME dossier ecrasait deja le fichier precedent).
# Comment il sera utilise (apercu) :
# - infrastructure/exporters/{json,csv,html}_exporter.py appellent
#   resolve_destination_file(job, content.summary, extension=<leur
#   format>) avant d'ecrire.
#---------------------------------------------------------------------->
