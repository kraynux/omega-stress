# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'entree Textual de l'application, cable par le composition root
(src/omega_stress/__main__.py)."""
from __future__ import annotations

import logging
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, cast

from omega_lib.terminal.models import RenderProfile
from omega_lib.terminal.policies import MINIMUM_USABLE_COLUMNS, MINIMUM_USABLE_ROWS
from textual.app import App, SystemCommand
from textual.binding import Binding
from textual.command import CommandPalette

from omega_stress.application.queries.detect_terminal import detect_terminal
from omega_stress.interfaces.tui.controllers import theme_controller
from omega_stress.interfaces.tui.controllers.startup_controller import (
    StartupState,
    resolve_startup_state,
)
from omega_stress.interfaces.tui.rendering.stylesheet_loader import load_paths_for
from omega_stress.interfaces.tui.rendering.textual_theme_builder import build_all_textual_themes
from omega_stress.interfaces.tui.screens.help_screen import HelpScreen
from omega_stress.interfaces.tui.screens.home import HomeScreen
from omega_stress.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_stress.interfaces.tui.screens.settings_screen import DEFAULT_SCREENSHOT_DIR_KEY
from omega_stress.interfaces.tui.screens.splash import SplashScreen
from omega_stress.interfaces.tui.screens.terminal_warning import TerminalWarningScreen

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.screen import Screen

    # Import reserve au typage statique (voir interfaces/cli/commands/
    # run_command.py pour la justification complete de ce motif) : cette
    # App reste construite avec un DependencyContainer deja assemble par
    # app/bootstrap.py, jamais assemble ni importe ici a l'execution.
    from omega_stress.app.dependency_container import DependencyContainer

TITLE = "🗲 OMEGA-STRESS"


class OmegaStressApp(App[None]):
    """Application TUI d'omega-stress : resout theme/profil de rendu au
    demarrage, puis enchaine demarrage -> (avertissement terminal) -> accueil."""

    TITLE = TITLE
    BINDINGS = [
        ("t", "cycle_theme", "Theme suivant"),
        ("a", "help", "Aide"),
        ("r", "refresh_terminal", "Rafraichir"),
        ("q", "quit", "Quitter"),
        Binding("ctrl+p", "command_palette", "Palette de commandes", show=False),
        Binding(
            "ctrl+q",
            "quit",
            "Quitter",
            show=False,
            tooltip="Quitter l'application (avec confirmation).",
        ),
    ]

    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self._startup_state = resolve_startup_state(
            terminal_detector=container.terminal_detector,
            settings_store=container.settings_store,
        )
        render_profile = RenderProfile(self._startup_state.terminal.render_profile)
        css_path = cast("list[str | PurePath]", load_paths_for(render_profile))
        super().__init__(css_path=css_path)
        for theme in build_all_textual_themes():
            self.register_theme(theme)
        self.theme = self._startup_state.theme.theme_name

    def on_mount(self) -> None:
        self.push_screen(SplashScreen(container=self._container), self._after_splash)

    def _after_splash(self, _result: None) -> None:
        terminal = self._startup_state.terminal
        too_small = terminal.columns < MINIMUM_USABLE_COLUMNS or terminal.rows < MINIMUM_USABLE_ROWS
        if terminal.render_profile == RenderProfile.MONO.value or too_small:
            message = (
                f"Terminal detecte : {terminal.family} ({terminal.columns}x{terminal.rows}). "
                f"Rendu applique : {terminal.render_profile}."
            )
            self.push_screen(TerminalWarningScreen(message=message), self._show_home)
        else:
            self._show_home(None)

    def _show_home(self, _result: None) -> None:
        self.push_screen(HomeScreen(container=self._container))

    def action_cycle_theme(self) -> None:
        current_profile = RenderProfile(
            self._container.settings_store.get("render_profile", RenderProfile.STANDARD.value)
        )
        status = theme_controller.cycle_theme(
            self.theme,
            direction=1,
            render_profile=current_profile,
            settings_store=self._container.settings_store,
        )
        self.theme = status.theme_name

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_refresh_terminal(self) -> None:
        """Touche `r` : redetecte la taille/famille du terminal (le
        sous-titre du Header ne se met sinon a jour QUE sur un changement
        de theme, voir watch_theme() — jamais sur un redimensionnement
        reel du terminal) et le journalise via une notification."""
        terminal = detect_terminal(terminal_detector=self._container.terminal_detector)
        self._startup_state = StartupState(terminal=terminal, theme=self._startup_state.theme)
        self._update_sub_title()
        self.notify(
            f"{terminal.family} ({terminal.columns}x{terminal.rows})", title="Terminal rafraichi"
        )

    def _update_sub_title(self) -> None:
        terminal = self._startup_state.terminal
        self.sub_title = f"{self.theme} | {terminal.columns}x{terminal.rows}"

    def watch_theme(self, _theme_name: str) -> None:
        """Tient le sous-titre du Header a jour (theme actif + taille du
        terminal detectee), sur CHAQUE changement de theme — y compris
        celui fait par __init__ au demarrage. Header lit self.app.sub_title
        de facon reactive (widget Textual standard), aucun ecran n'a besoin
        de s'en soucier individuellement."""
        self._update_sub_title()

    def action_command_palette(self) -> None:
        """Surcharge App.action_command_palette() : meme comportement,
        juste un texte d'invite en francais (Textual ne l'expose pas via
        un ClassVar, seulement via le constructeur de CommandPalette)."""
        # cast : App[object] attendu par is_open(), App[None] fourni — un
        # defaut de variance dans les annotations de Textual lui-meme (son
        # propre action_command_palette() a exactement le meme appel).
        if self.use_command_palette and not CommandPalette.is_open(cast("App[object]", self)):
            self.push_screen(
                CommandPalette(id="--command-palette", placeholder="Rechercher une commande…")
            )

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Traduit les commandes systeme de Textual (Theme/Quit/Keys/
        Screenshot, toujours en anglais par defaut, y compris quand le
        reste de l'application est en francais) plutot que d'appeler
        super() — PAS de traduction 1 pour 1 : Agrandir/Reduire
        (Maximize/Minimize) sont deliberement omises, voir INFO DEV."""
        yield SystemCommand("Theme", "Changer le theme actif", self.action_change_theme)
        yield SystemCommand(
            "Quitter", "Quitter l'application (avec confirmation)", self.action_quit
        )
        if screen.query("HelpPanel"):
            yield SystemCommand(
                "Raccourcis", "Masquer l'aide des raccourcis", self.action_hide_help_panel
            )
        else:
            yield SystemCommand(
                "Raccourcis",
                "Afficher l'aide du widget selectionne et les raccourcis disponibles",
                self.action_show_help_panel,
            )
        yield SystemCommand(
            "Capture d'ecran",
            "Enregistrer une capture SVG de l'ecran courant",
            lambda: self.set_timer(0.1, self._deliver_screenshot_to_configured_dir),
        )

    def _deliver_screenshot_to_configured_dir(self) -> None:
        """Livre la capture d'ecran courante dans le dossier configure
        (Reglages -> Captures d'ecran, DEFAULT_SCREENSHOT_DIR_KEY), a
        defaut self._container.screenshot_dir (var/screenshots/) — bug
        reel rapporte : sans `path=` explicite, App.deliver_screenshot()
        sauvegarde dans le dossier Telechargements de l'utilisateur (voir
        infrastructure/config/paths.py::screenshots_dir()). Cree le
        dossier au besoin (mkdir), meme convention que les exporters
        (infrastructure/exporters/*.py) pour leur propre destination."""
        configured = self._container.settings_store.get(
            DEFAULT_SCREENSHOT_DIR_KEY, str(self._container.screenshot_dir)
        )
        directory = Path(configured or self._container.screenshot_dir)
        directory.mkdir(parents=True, exist_ok=True)
        self.deliver_screenshot(path=str(directory))

    async def action_quit(self) -> None:
        """Surcharge App.action_quit() (touche `q`, signature async imposee
        par la classe de base) : demande confirmation au lieu de fermer
        immediatement (voir screens/quit_confirm.py)."""
        self.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.exit()

    def _handle_exception(self, error: Exception) -> None:
        """Filet de securite unique (ARCHITECTURE.md §5.4) : toute
        exception technique non prevue (ex. StorageError d'un export) est
        journalisee puis affichee comme notification generique, sans
        jamais fermer l'application ni montrer de trace Python brute.
        Redefinit un point d'extension prive de Textual (App._handle_exception,
        appele depuis _process_messages/_handle_batch_exceptions) faute de
        hook public equivalent (voir INFO DEV, Points cles) : c'est le
        SEUL endroit du projet a le faire."""
        logging.getLogger("omega_stress").error("Exception non prevue", exc_info=error)
        self.notify(
            str(error) or type(error).__name__,
            title="Erreur inattendue",
            severity="error",
            timeout=10,
        )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Racine Textual de l'interface : resout l'etat de demarrage (theme,
#   profil de rendu), enregistre les 10 themes du catalogue, enchaine
#   (avertissement terminal) -> accueil, expose le raccourci global de
#   cyclage de theme, et est le filet de securite unique pour toute
#   exception technique non prevue (§5.4, _handle_exception()).
# Pourquoi dans interfaces/tui/ (charte) :
# - Seul fichier autorise, avec rendering/, a combiner l'API Textual et
#   les donnees de theme/terminal — jamais construit ni importe par
#   app/dependency_container.py (le sens de dependance va toujours de
#   app/ vers interfaces/, jamais l'inverse).
# Ce qu'il ne contient PAS :
# - Aucune construction du DependencyContainer : recu tout assemble en
#   parametre du constructeur, construit par app/bootstrap.py.
# - Aucune degradation de PALETTE dynamique (reduced/mono) via
#   rendering/textual_theme_builder.py::build_textual_theme_from_palette()
#   quand le profil de rendu change en cours de session (ex. bascule
#   manuelle depuis screens/settings_screen.py) : seule la degradation
#   STRUCTURELLE (styles/{reduced,mono}.tcss, deja appliquee au demarrage
#   via CSS_PATH) est cablee dans cette V1 — la re-teinte a chaud reste un
#   axe d'amelioration explicitement differe, pas un oubli silencieux.
# Points cles :
# - css_path est passe a super().__init__(css_path=...) plutot
#   qu'assigne a self.CSS_PATH (ClassVar chez Textual, non reassignable
#   par instance) : App.__init__ accepte directement ce parametre pour
#   surcharger la variable de classe, sans en avoir besoin ici.
# - push_screen(screen, callback) (jamais push_screen() en cascade sans
#   callback) : garantit que l'accueil n'apparait qu'apres dismiss() de
#   l'avertissement terminal quand celui-ci s'affiche.
# - Ecran splash retire le 2026-08-24 (screens/splash.py supprime), PUIS
#   reintroduit le 2026-08-25 (demande explicite : "on va reintroduire le
#   splash", voir finalisation.txt) : la sequence est desormais
#   SplashScreen -> (TerminalWarningScreen si terminal trop petit/mono) ->
#   HomeScreen, via _after_splash() (callback de push_screen(), jamais un
#   push_screen() en cascade sans callback — meme regle que pour
#   TerminalWarningScreen ci-dessus). La composition ASCII complete
#   (silhouette + cadre OMEGA-STRESS) vit maintenant exclusivement sur
#   SplashScreen (widgets/splash_hero.py) ; screens/home.py n'affiche
#   plus qu'un bandeau texte simplifie (widgets/home_wordmark.py) —
#   raison du changement : coherence visuelle avec les autres applications
#   Omega, qui affichent toutes ce type de composition sur un ecran de
#   demarrage dedie plutot que sur le menu principal lui-meme.
# - action_cycle_theme() (touche `t`) applique toujours direction=1 : le
#   cyclage arriere n'est disponible que depuis screens/settings_screen.py
#   (Select explicite), pas de raccourci clavier dedie en V1.
# - action_help() (touche `a`, 2026-08-24) pousse HelpScreen() sans
#   argument constructeur (contrairement aux autres ecrans, qui recoivent
#   tous container) : HelpScreen est un contenu statique, aucun appel a
#   application/ (voir son propre INFO DEV).
# - watch_theme()/action_quit() (2026-08-24) : voir INFO DEV de
#   screens/quit_confirm.py pour la raison de la confirmation de sortie.
#   _update_sub_title() (factorise le 2026-08-24 de watch_theme() pour
#   etre aussi appelable depuis action_refresh_terminal()) est le SEUL
#   endroit qui ecrit self.sub_title — aucun ecran ne le fait
#   individuellement, coherent avec Header qui le lit de facon reactive
#   (chrome global, pas une decision par ecran).
# - TITLE = "🗲 OMEGA-STRESS" (2026-08-24, majuscules + icone incluse dans
#   la chaine) : Header(icon=...) docke l'icone separement du titre
#   centre (HeaderIcon/HeaderTitle, deux widgets distincts chez Textual)
#   — resultat visuel "icone collee tout a gauche, titre au centre",
#   jamais un seul bloc. Inclure l'icone DANS la chaine de titre est le
#   seul moyen de les faire apparaitre cote a cote comme une unite ; les
#   12 ecrans ne passent donc plus icon="🗲" a Header() (retire le meme
#   jour), Header() lit App.TITLE tout seul.
# - action_refresh_terminal() (touche `r`, 2026-08-24) : le sous-titre du
#   Header ne se met a jour QUE sur un changement de theme (watch_theme(),
#   ci-dessus) — jamais sur un redimensionnement reel du terminal, Textual
#   ne redeclenche pas ce watcher tout seul. Reconstruit StartupState en
#   entier (frozen) plutot que de muter un champ : coherent avec le type
#   deja immutable partout ailleurs dans le projet.
# - action_command_palette()/get_system_commands() (2026-08-24) :
#   traduisent en francais la palette de commandes standard de Textual
#   (Ctrl+P) — placeholder, entree "palette" du footer (via le binding
#   explicite dans BINDINGS, qui remplace celui que Textual ajoute sinon
#   automatiquement pour l'action "command_palette") et les commandes
#   systeme elles-memes (Theme/Quitter/Raccourcis/Capture d'ecran), qui
#   restaient en anglais malgre le reste de l'interface deja en francais.
#   Agrandir/Reduire (Maximize/Minimize, 2026-08-24) RETIREES le
#   2026-08-25 plutot que traduites : bug reel rapporte ("sa sert a rien
#   et sa fait planter l'application, sa laisse un ecran vide, oblige de
#   partir") — screen.action_maximize()/action_minimize() sont des
#   actions Textual generiques, jamais concues pour ce projet (aucun
#   widget de cette application ne beneficie d'un agrandissement plein
#   ecran ; un Button/Select/DataTable agrandi seul, sans le reste du
#   formulaire, n'a pas de sens ici) — supprimer l'entree evite le
#   plantage plutot que de le corriger a la source (cote Textual, hors de
#   portee de ce projet). show=False sur ce binding precis (comme
#   le binding par defaut de Textual qu'il remplace) : Footer affiche
#   deja une entree dediee, dockee a droite, pour l'action
#   "command_palette" independamment de show — sans show=False elle
#   apparaissait deux fois (une fois via la liste normale des bindings, une
#   fois via cette entree dediee).
# - _deliver_screenshot_to_configured_dir() (2026-08-25, bug reel
#   rapporte : "chemin des screenshots en svg a modifier dans
#   var/screenshots/") : App.deliver_screenshot() sans `path=` sauvegarde
#   dans le dossier Telechargements de l'utilisateur (comportement par
#   defaut de Textual, jamais var/) — cette methode lit le dossier
#   configure (Reglages -> Captures d'ecran, screens/settings_screen.py::
#   DEFAULT_SCREENSHOT_DIR_KEY), a defaut container.screenshot_dir
#   (var/screenshots/, infrastructure/config/paths.py::screenshots_dir()),
#   cree le dossier au besoin (mkdir, meme convention que les exporters)
#   puis livre la capture dedans. Lue a CHAQUE capture (pas mise en cache)
#   pour refleter un changement de reglage fait entre deux captures sans
#   redemarrer l'application.
# - Binding "ctrl+q" (2026-08-25) : App.BINDINGS de Textual porte deja un
#   raccourci systeme ctrl+q -> quit avec description "Quit" et tooltip
#   anglais ("Quit the app and return to the command prompt.") — distinct
#   de notre propre `("q", "quit", "Quitter")` (touche differente, mais
#   MEME nom d'action, donc appelle deja notre action_quit() surchargee
#   quelle que soit la touche pressee). Redeclare ici avec la MEME touche
#   ctrl+q pour ne changer QUE le texte affiche (francais), pas le
#   comportement — visible dans le panneau d'aide integre de Textual
#   (commande "Raccourcis"), bug reel rapporte ("il y a encore de
#   l'anglais"). Voir aussi screens/_base.py::OmegaScreen, meme
#   correctif pour trois autres bindings herites de Screen.
# - _handle_exception() (2026-08-24) redefinit App._handle_exception,
#   prive mais seul point d'appel reel (App.run_worker/exit_on_error=True
#   par defaut, App._process_messages) : Textual n'expose aucun hook
#   public equivalent (pas de on_exception()) dans cette version. Avant
#   ce correctif, TOUTE exception non catchee dans un worker d'ecran (ex.
#   StorageError d'un export vers un chemin invalide) faisait planter
#   toute l'application via Textual::_fatal_error() (Rich Traceback +
#   fermeture immediate) — bug reel observe le 2026-08-24 sur un export
#   HTML vers un dossier existant plutot qu'un fichier. Ne remplace pas
#   la traduction en Result/DomainError deja en place partout ailleurs
#   (§5.1) : un echec metier attendu ne devrait jamais atteindre ce
#   point ; s'il le fait souvent pour un meme cas, c'est ce cas qui doit
#   etre requalifie, pas ce filet qu'il faut muscler (§5.4, derniere
#   phrase).
# Comment il sera utilise :
# - src/omega_stress/__main__.py (composition root), quand aucune
#   sous-commande CLI n'est reconnue (voir son propre INFO DEV pour le
#   detail du dispatch).
#---------------------------------------------------------------------->
