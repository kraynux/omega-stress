# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Classe de base partagee par tous les ecrans navigables (retour clavier)."""
from __future__ import annotations

from textual.binding import Binding
from textual.screen import Screen


class OmegaScreen(Screen[None]):
    """Ecran navigable standard : ajoute `echap` -> retour a tous les
    ecrans qui en heritent, sans qu'aucun n'ait a redeclarer son propre
    binding. Ne remplace jamais le bouton "Retour" existant (meme action,
    juste un second chemin clavier) — voir chaque ecran pour le detail
    metier, ce fichier ne connait rien du domaine."""

    BINDINGS = [
        Binding("escape", "back", "Retour", show=True),
        Binding("tab", "app.focus_next", "Focus suivant", show=False),
        Binding("shift+tab", "app.focus_previous", "Focus precedent", show=False),
        Binding("ctrl+c,super+c", "screen.copy_text", "Copier le texte selectionne", show=False),
    ]

    def action_back(self) -> None:
        self.dismiss()

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Base commune de navigation clavier (touche `echap`) pour tous les
#   ecrans pousses sur la pile (donc "dismissables"), afin que le
#   Footer generique (rendu automatique par Textual a partir des
#   BINDINGS actifs, voir interfaces/tui/app.py) affiche toujours le
#   meme raccourci "Retour" partout.
# Pourquoi dans interfaces/tui/screens/ (charte) :
# - Widget de PRESENTATION pur, aucune logique metier — meme categorie
#   que les widgets partages (widgets/target_picker.py, widgets/
#   stat_card.py) : une base d'ecran partagee reste dans la meme
#   philosophie, ce n'est pas une entorse a la regle "3 ecrans de
#   lancement independants" (ARCHITECTURE.md §2, decision qui porte sur
#   la LOGIQUE DE LANCEMENT, pas sur le chrome de navigation).
# Ce qu'il ne contient PAS :
# - Aucune redefinition de dismiss() : action_back() appelle exactement
#   ce que chaque ecran appelait deja depuis son bouton "Retour"
#   (Screen.dismiss() sans argument, coherent avec Screen[None]).
# - screens/home.py (racine de la pile, aucun "retour" possible) et
#   screens/quit_confirm.py (son propre resultat bool, pas None)
#   n'heritent PAS de cette classe : home.py surcharge action_back()
#   pour la confirmation de sortie plutot que d'utiliser ce comportement
#   par defaut, quit_confirm.py est Screen[bool] par nature (voir son
#   propre fichier).
# Points cles :
# - Binding avec show=True : Textual::Footer lit deja
#   self.screen.active_bindings automatiquement (voir app.py) — aucun
#   widget Footer personnalise necessaire pour que "Retour" apparaisse.
# - tab/shift+tab/ctrl+c (2026-08-25) : re-declares avec les MEMES touches
#   que textual.screen.Screen.BINDINGS (une classe parente reecrit un
#   binding en fournissant la meme touche, mecanisme Textual standard,
#   deja utilise pour ctrl+p dans app.py) — uniquement pour remplacer
#   leur description ANGLAISE par defaut ("Focus Next"/"Focus Previous"/
#   "Copy selected text", jamais traduites par Textual lui-meme) : bug
#   reel rapporte ("dans le menu aide raccourci, il y a encore de
#   l'anglais") — ces trois lignes apparaissent dans le panneau d'aide
#   integre de Textual (commande "Raccourcis"/touche `?`), pas dans
#   screens/help_screen.py (ecran propre a ce projet, deja entierement en
#   francais). show=False conserve : ces raccourcis ne doivent pas
#   apparaitre dans le Footer, seulement dans ce panneau d'aide.
# - "Quit" (App.BINDINGS, touche ctrl+q) et "Press button"
#   (textual.widgets.Button.BINDINGS, touche Entree) restent en anglais
#   dans ce meme panneau : le premier est corrige dans app.py (meme
#   mecanisme) ; le second exigerait une sous-classe Button dediee
#   substituee a TOUS les Button(...) du projet pour une seule chaine
#   peu visible (uniquement ce panneau, jamais la navigation normale) —
#   juge hors de proportion, deliberement laisse tel quel.
# Comment il sera utilise (apercu) :
# - Tous les ecrans pousses via push_screen() heritent de OmegaScreen
#   au lieu de Screen[None] directement.
#---------------------------------------------------------------------->
