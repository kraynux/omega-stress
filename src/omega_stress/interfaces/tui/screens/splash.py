# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran de demarrage : composition ASCII complete, avant l'accueil."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from omega_stress.interfaces.tui.widgets.splash_hero import LOGO_CENTER_COLUMN, SplashHero

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer


class SplashScreen(Screen[None]):
    """Premier ecran affiche au demarrage (2026-08-25, reintroduit — voir
    finalisation.txt : "on va reintroduire le splash"). N'importe quelle
    touche ou clic fait passer a la suite (avertissement terminal, puis
    accueil, voir app.py::on_mount())."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        render_profile = RenderProfile(
            self._container.settings_store.get("render_profile", RenderProfile.STANDARD.value)
        )
        with Middle(classes="omega-splash-middle"):
            with Center():
                yield SplashHero(render_profile=render_profile)
            yield Static(
                "Appuyez sur une touche pour continuer…", classes="omega-splash-prompt"
            )
        yield Footer()

    def on_mount(self) -> None:
        self.call_after_refresh(self._center_prompt_on_logo)

    def on_resize(self, event: events.Resize) -> None:
        self.call_after_refresh(self._center_prompt_on_logo)

    def _center_prompt_on_logo(self) -> None:
        hero = self.query_one(SplashHero)
        prompt = self.query_one(".omega-splash-prompt", Static)
        logo_center = hero.region.x + LOGO_CENTER_COLUMN
        offset = max(0, round(logo_center - prompt.size.width / 2))
        prompt.styles.margin = prompt.styles.margin._replace(left=offset)

    def on_key(self, event: events.Key) -> None:
        event.stop()
        self.dismiss()

    def on_click(self, event: events.Click) -> None:
        event.stop()
        self.dismiss()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Ecran de bienvenue purement decoratif, affiche une seule fois au
#   demarrage, avant tout autre ecran (avertissement terminal ou accueil).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Ecran de presentation pur, Screen[None] : aucun appel a application/,
#   se contente d'afficher widgets/splash_hero.py et de rendre la main a
#   l'appelant sur n'importe quelle touche/clic.
# Ce qu'il ne contient PAS :
# - Aucune temporisation automatique (pas de self.set_timer() pour
#   disparaitre seul) : uniquement une sortie explicite de l'utilisateur,
#   coherent avec le reste de l'application (jamais d'ecran qui change
#   tout seul sans action).
# Points cles :
# - event.stop() sur on_key()/on_click() (2026-08-25) : AVANT ce garde-fou,
#   la meme touche qui fait disparaitre ce splash pouvait continuer sa
#   propagation et etre interpretee une seconde fois par l'ecran suivant
#   (bug deja rencontre par le passe sur une premiere version de cet
#   ecran, avant sa suppression temporaire — "splash-keypress leak") :
#   corrige des cette reintroduction plutot que de le laisser reapparaitre.
# - render_profile lu directement depuis settings_store ici (pas
#   transmis par l'appelant) : cet ecran n'a pas de on_screen_resume()
#   (jamais revisitee, un seul affichage par session), donc pas besoin du
#   mecanisme set_render_profile() de home.py.
# - Positionnement de l'invite en DEUX temps (2026-08-25, deux bugs reels
#   successifs rapportes par capture d'ecran reelle) :
#   1) "probleme de centrage du texte en bas du splash" — un premier essai
#      faisait partager a SplashHero et l'invite un seul Middle()+Center() ;
#      l'invite (plus etroite que le pave ASCII) restait "collee a gauche"
#      du pave plutot que centree sur l'ecran (confirme par introspection,
#      meme x que le pave). Corrige en donnant a SplashHero son propre
#      Center() — ".omega-splash-middle" (styles/base.tcss) force en plus
#      Middle() a width:1fr (son defaut est width:auto, ambigu avec un
#      Center() 1fr dedans) — meme correctif applique en parallele sur
#      screens/home.py.
#   2) "le texte du bas n'est pas centre sur le logo, il est decale a
#      gauche" — une fois (1) corrige, l'invite ETAIT bien centree sur le
#      TERMINAL (donc sur SplashHero dans son ENSEMBLE, silhouette
#      comprise), mais SplashHero n'est PAS visuellement symetrique : la
#      silhouette alourdit son cote gauche, deplacant le centre VISUEL du
#      "logo" (cadre LINUX SERVER TEST + OMEGA-STRESS) a droite du centre
#      GEOMETRIQUE du widget entier — centrer l'invite sur le widget ne la
#      centre donc pas sur ce que l'oeil percoit comme le logo.
#      _center_prompt_on_logo() calcule directement, en Python, la marge
#      gauche necessaire pour aligner le CENTRE de l'invite sur
#      SplashHero.LOGO_CENTER_COLUMN (colonne du centre du logo SEUL,
#      silhouette et accroche du bas exclues — voir widgets/splash_hero.py)
#      plutot que de continuer a chercher une solution CSS pure : ce
#      widget n'a pas de symetrie geometrique simple qu'un align/Center()
#      generique puisse exploiter. call_after_refresh() (pas un appel
#      direct dans on_mount()) : hero.region/.size ne sont pas encore
#      fiables au moment ou Screen.on_mount() s'execute, meme raison deja
#      rencontree ailleurs dans ce projet (ex. l'ancien screens/home.py::
#      _center_hero_on_menu(), avant sa suppression). on_resize() rappelle
#      le meme calcul : un redimensionnement reel du terminal deplace la
#      position de SplashHero (toujours centre par son propre Center()),
#      donc la marge de l'invite doit etre recalculee, pas seulement fixee
#      une fois au demarrage.
# Comment il sera utilise :
# - interfaces/tui/app.py::on_mount(), tout premier ecran pousse.
#---------------------------------------------------------------------->
