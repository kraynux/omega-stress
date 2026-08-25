# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Indicateur de progression d'un run en cours (jauge + temps restant)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import ProgressBar, Static


class RunProgress(Vertical):
    """Jauge de progression pour un run en cours, masquee tant qu'aucun
    run n'est lance. Reutilise textual.widgets.ProgressBar (show_eta=True)
    plutot que de recalculer un decompte a la main : le rythme
    d'echantillonnage (domain/load/policies.py::SAMPLE_INTERVAL_SECONDS,
    1 seconde) avance en temps reel, l'ETA integree de Textual (calculee
    depuis la vitesse d'avancement observee) coincide donc avec le temps
    reellement restant."""

    DEFAULT_CSS = """
    RunProgress {
        height: 4;
    }
    RunProgress > #run-progress-label {
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="run-progress-label")
        yield ProgressBar(id="run-progress-bar", show_eta=True)

    def on_mount(self) -> None:
        self.display = False

    def start(self, *, total_seconds: float) -> None:
        """A appeler juste avant de lancer un run : affiche la jauge,
        (re)initialise son total sur la duree totale planifiee."""
        self.query_one("#run-progress-label", Static).update("Test en cours…")
        self.query_one(ProgressBar).update(total=total_seconds, progress=0)
        self.display = True

    def update_elapsed(self, at_second: float) -> None:
        """A appeler a chaque IntervalSample recu (voir
        _PanelProgressNotifier dans les 3 ecrans de lancement)."""
        self.query_one(ProgressBar).update(progress=at_second)

    def stop(self) -> None:
        """A appeler des que le run se termine (succes, echec, ou arret
        automatique) : masque de nouveau la jauge."""
        self.display = False

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Widget de presentation pur : affiche l'avancement d'un run en cours
#   (jauge + ETA), sans connaitre le pipeline ni le domaine — pilote de
#   l'exterieur par l'ecran de lancement (start()/update_elapsed()/stop()).
# Pourquoi dans interfaces/tui/widgets/ (charte) :
# - Meme categorie que widgets/progress_panel.py (deja existant, affiche
#   debit/erreurs/p95 par IntervalSample) : ce widget-ci affiche la
#   dimension TEMPS de la meme donnee, pas une duplication de
#   responsabilite.
# Ce qu'il ne contient PAS :
# - Aucune connaissance de IntervalSample ni de LoadPlan : ne recoit que
#   des float (secondes), convertis par l'appelant — reste reutilisable
#   sans dependre du domaine metier.
# Points cles :
# - total_seconds (duree totale planifiee) n'est JAMAIS transmis par
#   RunProgressNotifier.notify() (le port ne porte que l'ecoule, voir
#   ports/run_progress_notifier.py) : c'est toujours l'ecran de lancement
#   qui le connait deja (champ "Duree (minutes)" du formulaire, deja
#   valide avant meme l'appel de lancement) et le passe a start().
# - display=False par defaut (on_mount) : la jauge n'existe dans le DOM
#   qu'une fois composee, mais reste invisible jusqu'au premier start(),
#   pour ne pas alourdir visuellement le formulaire avant tout lancement.
# - DEFAULT_CSS height:4 (2026-08-25) : RunProgress (Vertical) heritait de
#   height:1fr par defaut, sans jamais etre corrige — bug reel rapporte et
#   confirme par capture d'ecran en terminal reel ("jauge... toujours
#   inactive, ni de compteur temps") : le cadre (border, deja ajoute plus
#   tot) restait visible mais totalement VIDE, ni le libelle "Test en
#   cours…" ni la barre/ETA de ProgressBar ne s'affichaient — memes
#   symptomes et meme famille de cause que widgets/stat_card.py (voir son
#   propre INFO DEV) : une hauteur/largeur "auto" ou "1fr" imbriquee ne se
#   mesure pas de facon fiable dans cet environnement Textual precis, une
#   valeur CHIFFREE contourne le probleme. 4 = bordure haute (1) + libelle
#   (1) + ProgressBar (1, deja height:1 fixe dans son propre DEFAULT_CSS
#   Textual) + bordure basse (1). Le libelle "#run-progress-label"
#   recoit aussi une hauteur chiffree explicite (1), meme precaution.
#   Bug NON reproduit en environnement de test (Pilot/export_screenshot()) :
#   uniquement visible sur un vrai terminal, d'ou la confirmation par
#   capture d'ecran fournie par l'utilisateur plutot que par un test
#   automatise ici.
# Comment il sera utilise (apercu) :
# - screens/request_panel.py, connection_panel.py, ramp_panel.py :
#   start() au clic sur "Lancer", update_elapsed() depuis
#   _PanelProgressNotifier.notify(), stop() une fois l'outcome recu.
#---------------------------------------------------------------------->
