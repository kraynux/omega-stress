# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Indicateur de progression d'un run en cours (jauge + temps restant)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import ProgressBar, Static


def _format_minutes_seconds(total_seconds: float) -> str:
    whole = max(0, round(total_seconds))
    minutes, seconds = divmod(whole, 60)
    return f"{minutes:02d}:{seconds:02d}"


class RunProgress(Vertical):
    """Jauge de progression pour un run en cours, masquee tant qu'aucun
    run n'est lance."""

    DEFAULT_CSS = """
    RunProgress {
        height: 4;
    }
    RunProgress > #run-progress-label {
        height: 1;
    }
    """

    _total_seconds: float = 0.0

    def compose(self) -> ComposeResult:
        yield Static("", id="run-progress-label")
        yield ProgressBar(id="run-progress-bar", show_eta=False)

    def on_mount(self) -> None:
        self.display = False

    def start(self, *, total_seconds: float) -> None:
        """A appeler juste avant de lancer un run : affiche la jauge,
        (re)initialise son total sur la duree totale planifiee."""
        self._total_seconds = total_seconds
        self.query_one("#run-progress-label", Static).update(
            f"Test en cours… (reste {_format_minutes_seconds(total_seconds)})"
        )
        self.query_one(ProgressBar).update(total=total_seconds, progress=0)
        self.display = True

    def update_elapsed(self, at_second: float) -> None:
        """A appeler a chaque IntervalSample recu (voir
        _PanelProgressNotifier dans les 3 ecrans de lancement)."""
        self.query_one(ProgressBar).update(progress=at_second)
        remaining = self._total_seconds - at_second
        label = self.query_one("#run-progress-label", Static)
        if remaining >= 0:
            label.update(f"Test en cours… (reste {_format_minutes_seconds(remaining)})")
        else:
            overrun = _format_minutes_seconds(-remaining)
            label.update(f"Test en cours… (depasse la duree prevue de {overrun})")

    def stop(self) -> None:
        """A appeler des que le run se termine (succes, echec, ou arret
        automatique) : masque de nouveau la jauge."""
        self.display = False

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Widget de presentation pur : affiche l'avancement d'un run en cours
#   (jauge + temps restant), sans connaitre le pipeline ni le domaine —
#   pilote de l'exterieur par l'ecran de lancement (start()/
#   update_elapsed()/stop()).
# Pourquoi dans interfaces/tui/widgets/ (charte) :
# - Meme categorie que widgets/progress_panel.py (deja existant, affiche
#   debit/erreurs/p95 par IntervalSample) : ce widget-ci affiche la
#   dimension TEMPS de la meme donnee, pas une duplication de
#   responsabilite.
# Ce qu'il ne contient PAS :
# - Aucune connaissance de IntervalSample ni de LoadPlan : ne recoit que
#   des float (secondes), convertis par l'appelant — reste reutilisable
#   sans dependre du domaine metier.
# - Aucun ETA base sur la vitesse observee (voir Points cles, correctif
#   du 2026-09-02) : le temps restant est calcule DIRECTEMENT
#   (total_seconds - at_second), jamais estime/extrapole.
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
# - show_eta=False / decompte maison (2026-09-02, bug reel rapporte a
#   TROIS reprises avec captures d'ecran : "le compteur decompte a partir
#   de 3mn alors que 1mn selectionne", persistant meme apres un premier
#   correctif visant un mauvais diagnostic — voir ci-dessous) :
#   textual.widgets.ProgressBar(show_eta=True) delegue a textual.eta.ETA,
#   qui ESTIME le temps restant a partir de la VITESSE OBSERVEE recemment
#   (regression sur une fenetre glissante de 60s). Deux proprietes de
#   notre usage rendent cette estimation structurellement peu fiable :
#   (1) les toutes premieres secondes d'un run (connexion a la cible,
#   premiers echantillons) sont presque toujours plus lentes que le
#   regime de croisiere, ce qui gonfle artificiellement l'estimation
#   initiale (typiquement x3 dans les rapports recus) ; (2) pour un Test
#   charge (rampe), le debit varie CONTINUELLEMENT par construction
#   (domain/load/policies.py, RampStep), rendant toute extrapolation
#   lineaire de "vitesse recente" intrinsequement instable (rapporte :
#   le decompte remonte et redescend sans jamais se stabiliser). Un
#   premier correctif (forcer ProgressBar.update(total=None) avant
#   chaque start() pour garantir un reset de l'estimateur entre deux
#   lancements consecutifs sur le meme ecran) n'a eu AUCUN effet observe
#   : le bug se produisait deja des le tout PREMIER lancement d'un ecran
#   fraichement ouvert, prouvant que la cause n'etait pas un report de
#   donnees d'un run precedent mais bien l'algorithme d'estimation
#   lui-meme, des sa premiere execution. Solution retenue : ne plus
#   estimer DU TOUT — total_seconds et at_second sont deja connus avec
#   certitude (le premier vient du formulaire deja valide, le second de
#   chaque IntervalSample recu), leur simple soustraction donne un temps
#   restant EXACT par rapport a la progression LOGIQUE du plan (pas une
#   prediction de temps horloge reel) : n'accelere ni ne ralentit jamais
#   sans raison, ne depend d'aucune fenetre glissante ni d'aucun
#   historique. Consequence assumee : si le generateur prend reellement
#   plus d'une seconde reelle pour produire un intervalle "1 seconde"
#   logique (limite de capacite locale, voir domain/load/policies.py::
#   GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL), le decompte
#   n'avance pas plus vite que le plan ne progresse reellement — signal
#   honnete plutot qu'un decompte lisse mais trompeur. update_elapsed()
#   affiche explicitement un "depasse la duree prevue de ..." des que
#   at_second > total_seconds (remaining negatif), plutot que de
#   silencieusement plafonner a 00:00 comme le ferait un decompte naif.
# Comment il sera utilise (apercu) :
# - screens/request_panel.py, connection_panel.py, ramp_panel.py :
#   start() au clic sur "Lancer", update_elapsed() depuis
#   _PanelProgressNotifier.notify(), stop() une fois l'outcome recu.
#---------------------------------------------------------------------->
