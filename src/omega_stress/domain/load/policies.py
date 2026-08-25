# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Politiques de bornage du sous-domaine load : durees, pre-check, echantillonnage.

Source produit : plan_omega-stress_v5.md, sections "Bornage fonctionnel" et
"Pre-check". Toute valeur ici modifiee doit l'etre en accord avec ce
document — voir ARCHITECTURE.md §2 (regle de placement des politiques) et
§11 (revue de PR : aucune valeur de seuil/duree/intensite en dehors de ce
fichier).
"""
from __future__ import annotations

from omega_stress.core.enums import IntensityLevel

SAMPLE_INTERVAL_SECONDS: float = 1.0
"""Frequence d'echantillonnage des metriques pendant un run. Constante de
domaine, pas un parametre libre en V1 (borne un run de 5 minutes maximum a
300 lignes de metriques)."""

PRECHECK_VALIDITY_HOURS: float = 24.0
"""Duree de validite d'un pre-check deja valide et date dans un profil
fige ; au-dela, un nouveau pre-check est redemande avant un niveau
Haut/Maximum. Valeur retenue depuis l'exemple donne dans le plan produit
("à définir, ex. 24 h") : seule valeur numerique du plan qui restait
explicitement ouverte, tranchee ici a 24h faute d'enjeu de securite a la
faire varier (ajustable sans impact d'architecture si besoin)."""

ALWAYS_AVAILABLE_DURATIONS_MINUTES: tuple[int, ...] = (1, 2, 3, 4, 5)
"""Durees proposees pour les niveaux Bas/Moyen, toutes disponibles sans
condition."""

GATED_DEFAULT_DURATIONS_MINUTES: tuple[int, ...] = (1, 3)
"""Durees par defaut pour les niveaux Haut/Maximum."""

GATED_EXTENDED_DURATION_MINUTES: int = 5
"""Duree supplementaire pour Haut/Maximum, seulement si le profil fige ou
le pre-check l'autorise explicitement."""

PRECHECK_MANDATORY_LEVELS: frozenset[IntensityLevel] = frozenset(
    {IntensityLevel.HAUT, IntensityLevel.MAXIMUM}
)
"""Niveaux pour lesquels le pre-check est automatique et obligatoire : le
run ne demarre pas si le pre-check echoue ou n'a pas ete execute (regle
unique aux trois familles de test, voir plan produit section Pre-check)."""

LOCAL_BOTTLENECK_RATIO_THRESHOLD: float = 0.9
"""Seuil retenu pour signaler un ecart significatif entre debit demande et
debit reel comme indice de goulot d'etranglement local (plan produit :
"un ecart significatif y vaut comme signal indirect", sans valeur chiffree
donnee). 10% d'ecart est l'interpretation retenue ici, faute de valeur
figee dans le document produit — a ajuster explicitement si une valeur
differente est tranchee plus tard, dans ce seul fichier. Utilise a la fois
en direct pendant un run (application/pipeline/degraded_mode.py) et a
posteriori dans un rapport (domain/reports/builders.py) : une seule
constante partagee, jamais deux seuils qui pourraient diverger."""

MINIMUM_VIABLE_CPU_COUNT: int = 2
"""Palier "minimum viable" du plan produit (section "Configuration
minimale du generateur") : nombre de coeurs CPU en dessous duquel la
capacite systeme locale est jugee DEGRADED plutot qu'AVAILABLE."""

MINIMUM_VIABLE_RAM_MB: int = 4096
"""Palier "minimum viable" du plan produit (4 Go) pour la memoire totale
detectee."""

MINIMUM_OPEN_FILES_SOFT_LIMIT: int = 512
"""Limite douce minimale de descripteurs de fichiers ouverts jugee
suffisante pour tenir une charge V1. Absente du plan produit (qui ne
chiffre que CPU/RAM) : choix operationnel propre a cette implementation,
place ici comme les autres seuils plutot que dans infrastructure/probe/
(ARCHITECTURE.md §11)."""


def allowed_durations_minutes(
    level: IntensityLevel, *, extended_authorized: bool = False
) -> tuple[int, ...]:
    """Durees autorisees (en minutes) pour un niveau d'intensite donne.

    extended_authorized reflete une autorisation deja acquise (profil fige
    l'autorisant explicitement, ou pre-check valide) permettant les 5
    minutes en Haut/Maximum. Ce n'est jamais une saisie libre : toujours un
    sous-ensemble des valeurs figees ci-dessus.
    """
    if level not in PRECHECK_MANDATORY_LEVELS:
        return ALWAYS_AVAILABLE_DURATIONS_MINUTES
    if extended_authorized:
        return (*GATED_DEFAULT_DURATIONS_MINUTES, GATED_EXTENDED_DURATION_MINUTES)
    return GATED_DEFAULT_DURATIONS_MINUTES


def is_precheck_mandatory(level: IntensityLevel) -> bool:
    """True si le niveau exige un pre-check automatique et obligatoire."""
    return level in PRECHECK_MANDATORY_LEVELS

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte les regles de bornage du sous-domaine load qui ne sont pas des
#   valeurs de charge elles-memes (celles-ci sont dans presets.py) : durees
#   autorisees, gating du pre-check, frequence d'echantillonnage, duree de
#   validite d'un pre-check.
# Pourquoi dans domain/load/ (charte) :
# - Ce sont des politiques de securite/produit au sens strict de
#   ARCHITECTURE.md §2 : elles figurent sous forme de tableau dans le
#   document produit, donc elles vivent ici, jamais dans infrastructure/ ou
#   interfaces/, meme si c'est l'infrastructure (runner) ou l'interface
#   (panneau de test) qui les consomme.
# Ce qu'il ne contient PAS :
# - Les valeurs de charge elles-memes (req/min, connexions, paliers de
#   rampe) : voir presets.py, un fichier separe par lisibilite meme si les
#   deux vivent dans le meme sous-domaine.
# - Aucune validation de plan complet (verifier qu'un LoadPlan concret
#   respecte ces regles est le role de domain/load/validators.py, qui
#   consomme ces fonctions plutot que de les redefinir).
# - Aucun appel a un pre-check reel (c'est application/commands/
#   run_precheck.py) : ce fichier ne fait que dire QUAND un pre-check est
#   obligatoire, jamais COMMENT l'executer.
# Points cles :
# - allowed_durations_minutes() est la seule source de verite pour les
#   durees proposees a l'utilisateur (TUI/CLI) et pour la validation cote
#   domaine — les deux doivent l'appeler, jamais dupliquer les tuples.
# - PRECHECK_VALIDITY_HOURS est la seule valeur du plan produit qui restait
#   explicitement a trancher ("à définir") ; documentee ci-dessus avec sa
#   justification pour rester traçable si elle doit etre revue.
# Comment il sera utilise (apercu) :
# - domain/load/validators.py (plan_validator, threshold_evaluator)
#   appellera allowed_durations_minutes() pour rejeter une duree hors
#   bornes.
# - application/pipeline/guards/precheck_guard.py appellera
#   is_precheck_mandatory() avant d'autoriser un lancement Haut/Maximum.
# - infrastructure/runner/async_worker.py publiera la progression au rythme
#   de SAMPLE_INTERVAL_SECONDS via le port run_progress_notifier.
# - application/pipeline/degraded_mode.py et domain/reports/builders.py
#   consomment tous deux LOCAL_BOTTLENECK_RATIO_THRESHOLD.
# - infrastructure/probe/local_probe.py consomme MINIMUM_VIABLE_CPU_COUNT,
#   MINIMUM_VIABLE_RAM_MB et MINIMUM_OPEN_FILES_SOFT_LIMIT pour classer les
#   Capability qu'il produit (jamais de seuil chiffre code en dur cote
#   infrastructure).
#---------------------------------------------------------------------->
