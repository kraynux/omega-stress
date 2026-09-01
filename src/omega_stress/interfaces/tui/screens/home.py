# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran d'accueil : menu principal vers les autres ecrans."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from omega_stress.interfaces.tui.screens._base import OmegaScreen
from omega_stress.interfaces.tui.screens.calibration_screen import CalibrationScreen
from omega_stress.interfaces.tui.screens.connection_panel import ConnectionPanelScreen
from omega_stress.interfaces.tui.screens.help_screen import HelpScreen
from omega_stress.interfaces.tui.screens.history import HistoryScreen
from omega_stress.interfaces.tui.screens.profiles import ProfilesScreen
from omega_stress.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_stress.interfaces.tui.screens.ramp_panel import RampPanelScreen
from omega_stress.interfaces.tui.screens.request_panel import RequestPanelScreen
from omega_stress.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_stress.interfaces.tui.screens.targets import TargetsScreen
from omega_stress.interfaces.tui.widgets.home_wordmark import HomeWordmark

if TYPE_CHECKING:
    from omega_stress.app.dependency_container import DependencyContainer

_MENU_ITEMS: tuple[tuple[str, str], ...] = (
    ("profiles", "Profils"),
    ("request", "Test requetes"),
    ("connection", "Test connexions"),
    ("ramp", "Test charge"),
    ("history", "Historique"),
    ("targets", "Cibles"),
    ("calibration", "Calibrage"),
    ("settings", "Reglages"),
    ("help", "Aide"),
    ("quit", "Quitter"),
)


class HomeScreen(OmegaScreen):
    """Menu principal, point de depart de toute navigation au demarrage
    (et terminal_warning.py avant, si applicable)."""

    BINDINGS = [
        Binding("up", "focus_previous_item", "Monter", show=False),
        Binding("down", "focus_next_item", "Descendre", show=False),
    ]

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-home-root"):
            with Center():
                yield HomeWordmark(render_profile=self._current_render_profile())
            with Center():
                with Vertical(classes="omega-home-menu") as menu:
                    for item_id, label in _MENU_ITEMS:
                        with Container(classes="omega-btn-frame"):
                            yield Button(label.upper(), id=item_id)
                menu.border_title = "MENU PRINCIPAL"
        yield Footer()

    def on_screen_resume(self) -> None:
        self.query_one(HomeWordmark).set_render_profile(self._current_render_profile())

    def _current_render_profile(self) -> RenderProfile:
        return RenderProfile(
            self._container.settings_store.get("render_profile", RenderProfile.STANDARD.value)
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help":
            self.app.push_screen(HelpScreen())
            return
        if event.button.id == "quit":
            self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)
            return
        screen = self._screen_for(event.button.id)
        if screen is not None:
            self.app.push_screen(screen)

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()

    def action_back(self) -> None:
        """Surcharge OmegaScreen.action_back() : l'accueil est la racine
        de la pile (rien a quoi "revenir"), `echap` ici demande donc la
        meme confirmation de sortie que la touche `q` (voir
        interfaces/tui/app.py::action_quit(), meme QuitConfirmScreen)."""
        self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.app.exit()

    def _screen_for(self, item_id: str | None) -> Screen[None] | None:
        if item_id == "profiles":
            return ProfilesScreen(container=self._container)
        if item_id == "request":
            return RequestPanelScreen(container=self._container)
        if item_id == "connection":
            return ConnectionPanelScreen(container=self._container)
        if item_id == "ramp":
            return RampPanelScreen(container=self._container)
        if item_id == "history":
            return HistoryScreen(container=self._container)
        if item_id == "targets":
            return TargetsScreen(container=self._container)
        if item_id == "calibration":
            return CalibrationScreen(container=self._container)
        if item_id == "settings":
            return SettingsScreen(container=self._container)
        return None

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Seul point de navigation initial vers les huit sous-parcours de
#   l'application (profils, trois lancements, historique, cibles,
#   reglages, aide), plus un bouton "Quitter" direct (2026-08-25).
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Ecran de navigation pur, aucun appel a application/ ici (chaque ecran
#   pousse gere lui-meme ses propres controllers).
# Ce qu'il ne contient PAS :
# - Aucun import retour vers HomeScreen depuis les six ecrans qu'il pousse
#   (evite un cycle d'imports) : le retour se fait via
#   Screen.dismiss()/self.app.pop_screen(), jamais en re-poussant
#   HomeScreen explicitement.
# Points cles :
# - push_screen() (pas switch_screen()) : chaque sous-ecran reste empile,
#   Escape/bouton "Retour" revient naturellement ici via dismiss()
#   (OmegaScreen.action_back(), _base.py).
# - action_back() (2026-08-24) est SURCHARGE ici (pas le comportement par
#   defaut de OmegaScreen) : cet ecran est la racine de la pile, dismiss()
#   n'aurait rien "en dessous" ; `echap` demande donc confirmation de
#   sortie (memes QuitConfirmScreen/logique que app.py::action_quit(),
#   dupliques a l'identique plutot que factorises pour eviter un import
#   circulaire home.py<->app.py — home.py n'importe jamais app.py).
# - focus_previous()/focus_next() (2026-08-24) : Textual gere deja Tab
#   pour circuler entre les boutons, mais pas les fleches Haut/Bas entre
#   des Button simples (contrairement a un OptionList/DataTable) — ajoute
#   pour la navigation 100% clavier (voir plan produit, "navigation
#   flechee pour qui n'utilise pas la souris").
# - "help" (2026-08-24) est gere a part dans on_button_pressed(), pas dans
#   _screen_for() : HelpScreen() ne prend aucun container (contenu
#   statique, voir son propre fichier), contrairement aux six autres
#   ecrans que _screen_for() construit tous avec container=self._container
#   — melanger les deux dans la meme fonction aurait force un type de
#   retour optionnel supplementaire pour un seul cas particulier.
# - "quit" (2026-08-25) : meme raison que "help", gere a part dans
#   on_button_pressed() plutot que dans _screen_for() (QuitConfirmScreen
#   n'est pas un des six sous-parcours, et retourne un bool, pas un
#   Screen[None]) — reutilise _quit_if_confirmed(), le meme callback deja
#   utilise par action_back() (touche `echap`) : un seul chemin de
#   confirmation de sortie, que ce soit via le clavier ou ce bouton. Bug
#   reel demande explicitement ("rajouter un bouton quitter... pour
#   assumer une navigation 100% souris") : `echap` seul ne couvrait pas
#   un utilisateur qui n'utilise jamais le clavier.
# - HomeWordmark (2026-08-25, remplace HomeHero/widgets/home_hero.py,
#   supprime le meme jour — la composition ASCII complete vit desormais
#   sur screens/splash.py, voir widgets/splash_hero.py) recoit le profil
#   de rendu deja resolu (meme lecture settings_store que app.py::
#   action_cycle_theme()) : le widget lui-meme ne connait pas le
#   DependencyContainer (voir son propre INFO DEV), decide seulement
#   s'il s'affiche selon ce qu'on lui donne.
# - _current_render_profile() (2026-08-25) factorise cette lecture entre
#   compose() (premier montage) et on_screen_resume() (voir plus bas) :
#   une seule source de verite pour comment ce profil est resolu ici.
# - on_screen_resume() (2026-08-25) : bug reel rapporte ("je change le
#   profil de rendu dans Reglages, je reviens a l'accueil, l'ascii ne
#   s'affiche jamais, quel que soit le profil choisi") — compose() d'un
#   Screen ne s'execute qu'une seule fois, au tout premier montage
#   (app.py ne pousse HomeScreen qu'une fois ; y revenir depuis un ecran
#   empile revele l'instance EXISTANTE via dismiss(), sans jamais rappeler
#   compose()). Le render_profile passait donc au constructeur de
#   HomeWordmark UNE SEULE FOIS, fige pour toute la session, meme apres un
#   changement fait ensuite dans Reglages. on_screen_resume() relit l'etat
#   courant et le pousse dans le widget deja construit via
#   HomeWordmark.set_render_profile() (voir son propre INFO DEV) a chaque
#   retour sur cet ecran.
# - Refonte complete de la disposition (2026-08-25, demande explicite —
#   voir finalisation.txt : "je suis pas satisfait de la presentation,
#   elle decorele trop des autres application OMEGA") : l'ancienne
#   disposition deux colonnes (menu a gauche, composition ASCII a droite,
#   avec un calcul Python de marge pour les centrer l'un sur l'autre) est
#   entierement abandonnee. Desormais un simple empilement vertical —
#   HomeWordmark, puis le bloc de boutons (".omega-home-menu") — le tout
#   centre VERTICALEMENT par ".omega-home-root" (styles/base.tcss,
#   "align: center middle", height:1fr).
# - Titre "MENU PRINCIPAL" EMBARQUE DANS LE CONTOUR (2026-08-25, remplace
#   un Static separe dans son propre encadre — demande explicite : "on
#   enleve le petit container menu principal... MENU PRINCIPAL est un
#   element du contour... effet elements de console ou de dashboard") :
#   `menu.border_title = ...` (Widget.border_title, fonctionnalite
#   NATIVE Textual) peint ce texte directement dans la ligne de bordure
#   superieure du bloc de boutons, jamais un widget separe — voir
#   styles/base.tcss (".omega-home-menu", border-title-*) pour la mise en
#   forme. `as menu` (motif `with Vertical(...) as menu:`) capture
#   l'instance pour lui assigner border_title APRES avoir compose ses
#   boutons enfants — l'ordre n'a pas d'importance fonctionnelle ici
#   (border_title est un attribut d'affichage, pas structurel), mais
#   suivre l'ordre naturel de lecture du compose() reste plus clair.
# - Center() individuel par element (2026-08-25) : un premier essai
#   comptait sur "align: center middle" de ".omega-home-root" SEUL pour
#   centrer aussi HORIZONTALEMENT chacun des elements empiles (a
#   l'epoque trois : bandeau, titre "MENU PRINCIPAL" separe, boutons —
#   le titre a depuis fusionne dans le contour du bloc de boutons, voir
#   plus haut, mais le meme risque vaudrait pour tout nouvel element
#   ajoute ici) — insuffisant en pratique, bug reel rapporte par capture
#   d'ecran reelle ("probleme de centrage... sur le menu principal") et
#   confirme par introspection (.region) : un Vertical avec PLUSIEURS
#   enfants de largeurs differentes ne centre que le bloc entier sur la
#   largeur du plus large d'entre eux (le bandeau), les autres restant
#   colles au bord GAUCHE de ce bloc plutot que centres chacun sur leur
#   propre largeur — meme famille de divergence CSS-declaree/
#   rendu-reel deja rencontree ailleurs dans ce fichier, cette fois sur
#   un align multi-enfants plutot qu'un align mono-enfant. Corrige en
#   enveloppant CHAQUE element dans son propre `with Center():` (au lieu
#   d'un seul partage) : Center() est width:1fr par defaut, chaque
#   instance centre alors reellement son unique enfant sur la largeur
#   complete de ".omega-home-root" (elle-meme deja 1fr, pas auto — donc
#   aucune ambiguite de dimensionnement circulaire, contrairement au cas
#   ou Center() est plutot pose comme enfant direct d'un parent
#   auto-largeur, voir styles/base.tcss ".omega-confirm-buttons").
# - Libelles de boutons en MAJUSCULES (".upper()", 2026-08-25, demande :
#   "titre des boutons en majuscules") : transformation Python au moment
#   de construire chaque Button — Textual n'a pas d'equivalent CSS
#   text-transform, meme convention deja utilisee ailleurs dans le projet
#   pour les titres d'ecran (".omega-title").
# - "calibration" (2026-09-01) : ajoute entre "targets" et "settings" —
#   ecran jamais accessible avant ce jour ("je vois pas de menu
#   calibrage", bug reel rapporte), le mecanisme lui-meme
#   (domain/calibration/, application/commands/run_calibration.py)
#   existait deja mais n'etait relie a aucune navigation TUI/CLI.
# Comment il sera utilise :
# - interfaces/tui/app.py, apres screens/splash.py (et apres
#   terminal_warning.py si applicable).
#---------------------------------------------------------------------->
