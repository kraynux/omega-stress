# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Composition ASCII complete (silhouette degradee + cadre OMEGA-STRESS),
affichee UNIQUEMENT par screens/splash.py (2026-08-25, demande explicite :
"reintroduire le splash et mettre l'ascii suivant... et supprimer celui sur
du menu general" — voir finalisation.txt, remplace l'ancien
widgets/home_hero.py, qui n'existe plus). screens/home.py affiche desormais
un simple bandeau texte, voir widgets/home_wordmark.py."""
from __future__ import annotations

from textual import events
from textual.widgets import Static

from omega_stress.core.enums import RenderProfile

_FONT_TOKEN = "$foreground"
"""Jeton de theme resolu par le moteur de markup de Content (Textual 8.x) :
garantit un contraste clair dans les 10 themes du catalogue, meme
mecanisme deja verifie dans l'ancien widgets/home_hero.py (voir historique
git)."""

# Chaque ligne = (indentation avant la silhouette, glyphes de la
# silhouette, colonne absolue de debut du cadre OMEGA-STRESS). Extrait
# PROGRAMMATIQUEMENT de finalisation.txt (2026-08-25, fourni par
# l'utilisateur) pour eviter toute erreur de transcription manuelle sur un
# art aussi dense — voir Points cles de l'INFO DEV pour la methode.
# Ne couvre QUE les 14 premieres lignes (cadre titre + cadre OMEGA-STRESS) :
# la 15e (accroche "CHARGES | ...") est positionnee separement plus bas,
# voir son propre commentaire.
_SILHOUETTE_ROWS_HEAD: tuple[tuple[int, str, int], ...] = (
    (18, "+-", 33),
    (16, "+%-", 33),
    (12, ".=#%#-", 33),
    (9, ".+%%%#:", 40),
    (7, ".+%%%%*:", 25),
    (5, ":*%%%%%*=======:", 25),
    (2, ":*#%%%%%%%%%%%%%+.", 25),
    (0, ":*%%%%%%%%%%%%%%+.", 25),
    (7, "-#%%%%%=.", 25),
    (6, "=%%%%=.", 21),
    (4, "-%%%%=", 21),
    (3, "=%%#=", 21),
    (2, "=#*-", 21),
    (1, ":+-", 21),
)

_FRAME_BOX_HEAD = (
    "┌────────────────────────┐",
    "│    LINUX SERVER TEST   │",
    "└────────────────────────┘",
    "▓▒░v1.0░▒▓",
    "┌─────────────────────────────────────────┐",
    "│ ┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ │",
    "│ │║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ │",
    "│ └╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘ │",
    "└───────────────────┐┌────────────────────┘",
    "┌───────────────────────┘└────────────────────────┐",
    "│ ┌╦═══╦┐ ┌═╤╦╤═┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ │",
    "│ └╩═══╦┐   │║│   │╠══╦╩┘ ├╬══    └╩═══╦┐ └╩═══╦┐ │",
    "│ └╩═══╩┘   ╧╩╧   └╩  ╚═┘ └╩═══╩┘ └╩═══╩┘ └╩═══╩┘ │",
    "└─────────────────────────────────────────────────┘",
)
"""Compose identique a l'ancien widgets/home_hero.py::_ART_LINES (verifie
caractere pour caractere lors de ce correctif) : seule la mise en couleur
et l'ajout de la silhouette a gauche changent, jamais ce dessin lui-meme."""

_TAGLINE = "CHARGES | CONNEXIONS | REQUETES | EXPORTS | ANALYSES"

_LOGO_CENTER_COLUMN: float = (
    min(frame_col for _, _, frame_col in _SILHOUETTE_ROWS_HEAD)
    + max(
        frame_col + len(frame_row)
        for (_, _, frame_col), frame_row in zip(
            _SILHOUETTE_ROWS_HEAD, _FRAME_BOX_HEAD, strict=True
        )
    )
) / 2
"""Colonne (relative au bord GAUCHE de ce widget) du centre visuel du
"logo" (cadre LINUX SERVER TEST + cadre OMEGA-STRESS) — SANS la
silhouette a gauche. Sert de reference commune a l'accroche du bas ET a
screens/splash.py::_center_prompt_on_logo(), voir LOGO_CENTER_COLUMN
(alias public) plus bas."""

_TAGLINE_COLUMN = round(_LOGO_CENTER_COLUMN - len(_TAGLINE) / 2)
"""Colonne de l'accroche du bas (2026-08-25, DEUXIEME bug reel rapporte
par capture d'ecran reelle sur ce meme point) : un premier correctif
alignait l'accroche sur le taquet de tabulation d'origine
(finalisation.txt, colonne 33, meme colonne que le cadre "LINUX SERVER
TEST") — mathematiquement fidele au fichier source, mais visuellement
rejete ("il est parti carrement dans l'autre sens") : l'accroche (54
caracteres) est bien plus LARGE que le cadre "LINUX SERVER TEST" (27
caracteres), un alignement a gauche stricte la fait donc deborder tres
loin a droite du cadre, asymetrique. Cette colonne CENTRE l'accroche sur
_LOGO_CENTER_COLUMN a la place — meme reference que l'invite du bas de
screens/splash.py, choix coherent avec elle plutot qu'une troisieme regle
d'alignement differente."""

_SILHOUETTE_ROWS: tuple[tuple[int, str, int], ...] = (
    *_SILHOUETTE_ROWS_HEAD,
    (0, ":-", _TAGLINE_COLUMN),
)
_FRAME_BOX = (*_FRAME_BOX_HEAD, _TAGLINE)

_FULL_BRIGHT_ROWS = frozenset({0, 2, 4, 8, 9, 13})
"""Lignes de cadre PUR (bordure du titre, cadre externe OMEGA/STRESS) :
entierement "clair" (demande : "son contour en clair... le contour de
omega-stress en clair")."""

_MIDDLE_BRIGHT_ROWS = frozenset({6, 11})
"""Lignes du MILIEU de chaque lettre OMEGA/STRESS (le corps de la police,
pas son contour) : entierement "clair" (demande : "la ligne du milieu du
texte omega et stress en clair"), inchange depuis l'ancien home_hero.py."""

_OUTER_PIPE_BRIGHT_ROWS = frozenset({1, 5, 7, 10, 12})
"""Lignes ou seuls les DEUX "│" exterieurs (le cadre) passent en clair,
le contenu entre les deux (texte "LINUX SERVER TEST", ou hauts/bas des
lettres OMEGA/STRESS) reste "vif" (couleur $accent par defaut, non
marque) : demande "le texte linux server test en vif, son contour en
clair" + "les autres lignes du bas et haut en vif"."""


def _colorize_frame_row(index: int, row: str) -> str:
    if index in _FULL_BRIGHT_ROWS or index in _MIDDLE_BRIGHT_ROWS:
        return f"[{_FONT_TOKEN}]{row}[/]"
    if index in _OUTER_PIPE_BRIGHT_ROWS:
        first = row.index("│")
        last = row.rindex("│")
        return (
            row[:first]
            + f"[{_FONT_TOKEN}]{row[first]}[/]"
            + row[first + 1 : last]
            + f"[{_FONT_TOKEN}]{row[last]}[/]"
            + row[last + 1 :]
        )
    if index == 14:
        return " | ".join(f"[{_FONT_TOKEN}]{word}[/]" for word in row.split(" | "))
    return row


def _colorize_silhouette(glyphs: str) -> str:
    """Nuance la silhouette plutot qu'un bloc de couleur uniforme (demande :
    "essaye de mettre des nuances sur l'eclair pour eviter un bloc couleur
    uniforme... seul les % sont de couleurs polices classic... les autres
    symboles descendre de une ou deux nuances") : "%" en $foreground (le
    "blanc" cite, voir _FONT_TOKEN), tout le reste de la silhouette (+#*=.:-)
    en "dim" — un style Rich standard qui assombrit la couleur heritee
    ($accent, definie sur le widget lui-meme) d'un cran, sans dependre d'un
    jeton de theme supplementaire a ajouter aux 10 palettes. Les runs
    consecutifs de meme categorie sont regroupes en un seul span (lisibilite
    du balisage, pas une contrainte de rendu)."""
    spans: list[str] = []
    run: list[str] = []
    run_is_bright: bool | None = None
    for char in glyphs:
        is_bright = char == "%"
        if is_bright != run_is_bright and run:
            text = "".join(run)
            spans.append(f"[{_FONT_TOKEN}]{text}[/]" if run_is_bright else f"[dim]{text}[/]")
            run = []
        run.append(char)
        run_is_bright = is_bright
    if run:
        text = "".join(run)
        spans.append(f"[{_FONT_TOKEN}]{text}[/]" if run_is_bright else f"[dim]{text}[/]")
    return "".join(spans)


def _build_art_markup() -> tuple[str, ...]:
    lines = []
    for index, ((lead, glyphs, frame_col), frame_row) in enumerate(
        zip(_SILHOUETTE_ROWS, _FRAME_BOX, strict=True)
    ):
        padding = " " * (frame_col - lead - len(glyphs))
        colored_frame = _colorize_frame_row(index, frame_row)
        lines.append(" " * lead + _colorize_silhouette(glyphs) + padding + colored_frame)
    return tuple(lines)


_ART_MARKUP = _build_art_markup()
_PLAIN_WIDTH = max(
    lead + len(glyphs) + (frame_col - lead - len(glyphs)) + len(frame_row)
    for (lead, glyphs, frame_col), frame_row in zip(_SILHOUETTE_ROWS, _FRAME_BOX, strict=True)
)
_MIN_TERMINAL_WIDTH = _PLAIN_WIDTH + 6
"""Marge minimale (contrairement a l'ancien home_hero.py, plus de colonne
de menu a cote : l'ecran splash n'affiche plus que ce bloc, centre seul —
la marge ne couvre donc plus qu'un espace de confort de chaque cote)."""

LOGO_CENTER_COLUMN: float = _LOGO_CENTER_COLUMN
"""Alias PUBLIC de _LOGO_CENTER_COLUMN (colonne, relative au bord GAUCHE
de ce widget, du centre visuel du "logo" — cadre LINUX SERVER TEST +
cadre OMEGA-STRESS — SANS la silhouette a gauche ni l'accroche du bas) :
bug reel rapporte par capture d'ecran reelle ("le texte du bas n'est pas
centre sur le logo, il est decale a gauche") : ce widget dans son
ENSEMBLE (silhouette comprise) n'est PAS visuellement symetrique (la
silhouette alourdit le cote gauche), donc centrer l'invite du bas sur la
largeur TOTALE du widget (ou sur le terminal, ce qui revient au meme
puisque le widget lui-meme est centre sur le terminal) ne l'aligne pas
avec ce que l'oeil percoit comme "le logo". Meme reference utilisee ICI
pour l'accroche "CHARGES | ..." (voir _TAGLINE_COLUMN plus haut) ET par
screens/splash.py::_center_prompt_on_logo() pour l'invite "Appuyez sur
une touche..." — une seule source de verite pour "le centre du logo",
jamais recalculee deux fois independamment."""


class SplashHero(Static):
    """Bloc decoratif plein ecran de screens/splash.py. Meme logique de
    masquage que l'ancien widgets/home_hero.py (profil MONO ou terminal
    trop etroit -> masque entierement, jamais de version compacte)."""

    def __init__(self, *, render_profile: RenderProfile) -> None:
        super().__init__("\n".join(_ART_MARKUP), classes="omega-splash-hero")
        self._render_profile = render_profile

    def on_mount(self) -> None:
        self._update_visibility()

    def on_resize(self, event: events.Resize) -> None:
        self._update_visibility()

    def _update_visibility(self) -> None:
        simplified = self._render_profile is RenderProfile.MONO
        too_narrow = self.app.size.width < _MIN_TERMINAL_WIDTH
        self.display = not (simplified or too_narrow)

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Bloc decoratif plein ecran de l'ecran de demarrage (screens/splash.py),
#   seul endroit qui l'utilise desormais.
# Pourquoi dans interfaces/tui/widgets/ (charte) :
# - Widget de presentation pure, comme l'ancien widgets/home_hero.py qu'il
#   remplace.
# Ce qu'il ne contient PAS :
# - Aucun dessin different du cadre OMEGA-STRESS existant (_FRAME_BOX est
#   VERIFIE identique caractere pour caractere a l'ancien home_hero.py::
#   _ART_LINES lors de ce correctif) : seule la silhouette a gauche et la
#   mise en couleur (nuancee plutot qu'un seul ton) sont nouvelles.
# - Aucune reconstruction dynamique par largeur de terminal (comme avant :
#   sous le seuil, le bloc disparait entierement).
# Points cles :
# - _SILHOUETTE_ROWS (lead, glyphes, colonne du cadre) extrait
#   PROGRAMMATIQUEMENT du fichier finalisation.txt fourni par
#   l'utilisateur (script Python jetable, pas de retranscription manuelle)
#   pour eviter tout decalage/erreur de copie sur un art aussi dense —
#   raison directe de la demande utilisateur ("pour eviter les problemes
#   de decalage de copier coller, les directives se trouvent dans le
#   fichier finalisation.txt").
# - Regles de couleur (2026-08-25, demande explicite, voir finalisation.txt) :
#   * Ligne du milieu OMEGA/STRESS (le corps de chaque lettre) : "clair"
#     ($foreground) — inchange depuis l'ancien widget.
#   * Hauts/bas des lettres OMEGA/STRESS et texte "LINUX SERVER TEST" :
#     "vif" (couleur $accent par defaut du widget, non marque).
#   * Cadre exterieur (bordure du titre, cadre externe OMEGA-STRESS, "│"
#     exterieurs des lignes de lettres et du titre) : "clair" — INVERSE
#     de la version precedente de home_hero.py, qui avait le texte du
#     titre en clair et son cadre en vif (bug de coherence signale :
#     "decorele trop des autres application OMEGA").
#   * "v1.0" : laisse en "vif" (aucune consigne specifique donnee, pas de
#     cadre propre a inverser — differe du choix precedent qui l'alignait
#     a tort sur le titre).
#   * Accroche du bas : mots en clair, "|" en vif — inchange.
# - Silhouette nuancee (pas un bloc uniforme) : "%" en $foreground, le
#   reste (+#*=.:-) en style Rich "dim" — voir _colorize_silhouette().
# Comment il sera utilise :
# - screens/splash.py, seul appelant.
#---------------------------------------------------------------------->
