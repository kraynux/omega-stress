# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'entree du package (`python -m omega_stress` et le script console `omega-stress`).

Veritable racine de composition : le seul module du projet qui importe a la
fois app/ (demarrage/arret) et interfaces/ (dispatch CLI). N'appartient a
aucune des 9 couches declarees (ni `app`, ni `interfaces`), donc n'est
contraint par aucun des contrats import-linter de couches — c'est
precisement pour cette raison que le cablage final vit ici plutot que dans
interfaces/cli/main.py (voir son INFO DEV pour l'historique de la
correction)."""
from __future__ import annotations

import sys

from omega_stress.app.bootstrap import bootstrap
from omega_stress.interfaces.cli.main import run as run_cli
from omega_stress.interfaces.tui.app import OmegaStressApp


def main(argv: list[str] | None = None) -> int:
    """Demarre l'application, dispatche vers le TUI (aucun argument) ou
    le CLI (au moins un argument), ferme proprement quelle que soit
    l'issue."""
    effective_argv = sys.argv[1:] if argv is None else argv
    app = bootstrap()
    try:
        if not effective_argv:
            OmegaStressApp(app.container).run()
            return 0
        return run_cli(app.container, effective_argv)
    finally:
        app.lifecycle.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Racine de composition finale : demarre l'application
#   (app/bootstrap.py) puis dispatche vers le TUI
#   (interfaces/tui/app.py::OmegaStressApp) ou le CLI
#   (interfaces/cli/main.py::run()), avec fermeture garantie dans un
#   `finally`.
# Pourquoi ici (charte) :
# - Convention Python standard (`python -m omega_stress`) ; c'est aussi la
#   cible du script console declare dans pyproject.toml
#   ([project.scripts] omega-stress = "omega_stress.__main__:main").
# - C'est le SEUL endroit du projet ou app/ et interfaces/ sont importes
#   ensemble : les deux sont des tiers independants dans le contrat
#   import-linter "Dependency Rule" (ni l'un ni l'autre n'est autorise a
#   importer l'autre), donc leur assemblage final doit necessairement
#   vivre en dehors des deux.
# Ce qu'il ne contient PAS :
# - Aucune logique propre : delegue integralement a bootstrap() et run().
# Points cles :
# - Une premiere version de ce fichier delegait directement a
#   interfaces/cli/main.py::main(), qui appelait lui-meme bootstrap() en
#   interne — import-linter a signale que cela rendait interfaces/
#   transitivement dependante d'infrastructure/ (sqlite3/httpx/jinja2),
#   violation reelle detectee en pratique (2026-08-24). Le demarrage a
#   ete remonte ici, seul point du projet legitime a connaitre les deux
#   cotes.
# - Regle de dispatch delibrement simple : AUCUN argument -> TUI (mode
#   interactif, l'usage le plus courant) ; AU MOINS UN argument -> CLI,
#   quel qu'il soit (une sous-commande reconnue, `--help`, ou une chaine
#   invalide qu'argparse lui-meme expliquera avec un message precis).
#   Ce fichier ne maintient donc jamais sa propre liste de sous-commandes
#   reconnues (profile/run/history/export) en parallele de
#   interfaces/cli/main.py::build_parser(), qui reste la seule source de
#   verite — un typo dans une sous-commande produit l'erreur argparse
#   habituelle, jamais un lancement silencieux du TUI a la place.
# Comment il sera utilise (apercu) :
# - `python -m omega_stress <sous-commande> ...`
# - Script console `omega-stress` (installe via pyproject.toml).
#---------------------------------------------------------------------->
