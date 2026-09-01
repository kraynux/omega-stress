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
fige ; au-dela, un nouveau pre-check est redemande avant un niveau gate
(optionnel ou obligatoire). Valeur retenue depuis l'exemple donne dans le plan produit
("à définir, ex. 24 h") : seule valeur numerique du plan qui restait
explicitement ouverte, tranchee ici a 24h faute d'enjeu de securite a la
faire varier (ajustable sans impact d'architecture si besoin)."""

ALWAYS_AVAILABLE_DURATIONS_MINUTES: tuple[int, ...] = (1, 2, 3, 4, 5)
"""Durees proposees pour les niveaux jamais gates (Faible/Bas/Moyen-Normal/
Haut-Fort), toutes disponibles sans condition."""

GATED_BASE_DURATIONS_MINUTES: tuple[int, ...] = (1, 2, 3)
"""Durees de base pour un niveau gate (optionnel ou obligatoire) —
disponibles que le pre-check soit valide ou non."""

GATED_EXTENDED_DURATIONS_MINUTES: tuple[int, ...] = (4, 5)
"""Durees supplementaires pour un niveau gate OPTIONNEL uniquement
(Puissant/Agressif), si le profil fige ou le pre-check l'autorise
explicitement — un niveau gate OBLIGATOIRE (Violent/Maximum) ne les
propose jamais : le pre-check y conditionne l'acces au niveau lui-meme,
pas une duree supplementaire (voir allowed_durations_minutes()
ci-dessous)."""

PRECHECK_OPTIONAL_LEVELS: frozenset[IntensityLevel] = frozenset(
    {IntensityLevel.PUISSANT, IntensityLevel.AGRESSIF}
)
"""Niveaux pour lesquels le pre-check est FACULTATIF : le run demarre sans,
mais le valider debloque GATED_EXTENDED_DURATIONS_MINUTES en plus des
durees de base."""

PRECHECK_MANDATORY_LEVELS: frozenset[IntensityLevel] = frozenset(
    {IntensityLevel.VIOLENT, IntensityLevel.MAXIMUM}
)
"""Niveaux pour lesquels le pre-check est automatique et obligatoire : le
run ne demarre pas si le pre-check echoue ou n'a pas ete execute (regle
unique aux trois familles de test). Distinct de PRECHECK_OPTIONAL_LEVELS
ci-dessus : ici le pre-check conditionne l'acces au niveau, pas une
duree etendue."""

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

GENERATOR_CPU_WARNING_THRESHOLD: float = 80.0
"""Seuil (pourcentage CPU du processus generateur, pic observe pendant
le run, deja normalise 0-100 sur l'ensemble des coeurs — voir domain/
runs/models.py::SystemSnapshot.cpu_percent_generator) au-dela duquel
domain/reports/builders.py ajoute une recommandation invitant a se
mefier du resultat — precurseur leger de la qualification
GENERATOR_LIMITED complete (Phase 5 du document calibrage-profils-
securite, pas encore construite). Seuil de RECOMMANDATION, pas d'arret :
ne declenche jamais abort_run(). Reste un pourcentage ABSOLU fixe,
contrairement a GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE ci-dessous
(corrige le 2026-09-01) : simplification assumee (un peu moins fiable
sur 4+ coeurs, ou un coeur pleinement sature ne declenche plus cette
recommandation) — a revoir si ce texte de rapport se revele trompeur en
pratique, mais aucun impact sur la securite du run (contrairement au
seuil d'arret, jamais un simple texte de recommandation)."""

# --- Phase 2 : garde-fous en direct (fenetres glissantes + ressources
# generateur) — source produit : omega-stress-calibrage-profils-
# securite.md, sections "Fenetres d'observation", "Politique d'arret par
# erreurs" et "Politique d'arret locale". Seuils ABORT uniquement (le
# document prevoit aussi des paliers avertissement/throttle, non
# construits ici — decision produit, voir plan Phase 2). Jamais
# configurables par profil : planchers de securite fixes, memes
# raisons que MINIMUM_VIABLE_CPU_COUNT etc. ci-dessus.

SLIDING_WINDOW_SECONDS: float = 30.0
"""Fenetre principale d'evaluation des taux d'erreur/timeout."""

CRITICAL_WINDOW_SECONDS: float = 10.0
"""Fenetre courte, evaluee en plus de la fenetre principale pour reagir
plus vite a un pic recent et concentre."""

MINIMUM_REQUESTS_FOR_WINDOW_EVALUATION: int = 20
"""Nombre de REQUETES (pas d'echantillons) cumulees sur une fenetre en
dessous duquel aucun taux n'est calcule — evite qu'un tout debut de run
avec 2 requetes dont 1 en erreur (50%) declenche un arret sur un
echantillon statistiquement non significatif."""

WINDOW_TIMEOUT_RATE_ABORT_THRESHOLD: float = 0.25
"""Document : "Timeouts sur fenetre 30s" palier Abort (>=25%)."""

WINDOW_HTTP_5XX_RATE_ABORT_THRESHOLD: float = 0.15
"""Document : "Erreurs HTTP 5xx sur fenetre 30s" palier Abort (>=15%)."""

WINDOW_TOTAL_ERROR_RATE_ABORT_THRESHOLD: float = 0.30
"""Document : "Erreurs totales sur fenetre 30s" palier Abort (>=30%)."""

GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE: float = 0.95
"""Document : "CPU Omega-Stress" palier Abort (esprit ">=90%", voir
Points cles ci-dessous pour la correction) — exprime comme une fraction
de ce qu'UN SEUL coeur logique peut fournir (100 / nombre de coeurs),
jamais un pourcentage absolu fixe : le moteur asyncio est lie au GIL
(un seul coeur utilisable pour ce workload, quel que soit le nombre de
coeurs disponibles par ailleurs) — un seuil absolu de 90% sur
cpu_percent_generator (deja normalise 0-100 sur l'ensemble des coeurs,
voir domain/runs/models.py::SystemSnapshot) serait systematiquement
atteint sur une machine a 1 coeur des la moindre charge, et quasiment
inatteignable des 4 coeurs (~25% normalise au mieux pour un seul coeur
sature) — bug reel corrige le 2026-09-01 (un run "Maximum" s'arretait
au bout de 3s sur une machine a 4 coeurs, diagnostic ">90%", alors que
l'utilisation globale machine restait ~20%). Ce ratio reste valable
quel que soit le nombre de coeurs du poste qui execute Omega-Stress —
condition necessaire, la version etant destinee a etre distribuee sur
des machines heterogenes.

Releve de 0.85 a 0.95 le 2026-09-01 (meme jour, second correctif suite a
une nouvelle session de test utilisateur avec captures d'ecran) : mesure
empirique en session (CLI pur, sans Textual, contre un serveur de test
local, machine 4 coeurs SAINE) montre qu'un Test connexions Moyen (100
connexions, tout a fait normal) atteint deja ~22.6% de CPU generateur, et
Haut/Puissant (200-1000, throttles) PLAFONNENT autour de 24-25% — soit
la saturation NORMALE et attendue d'un client HTTP async Python sur son
seul coeur exploitable, jamais un signe de danger pour la machine (RAM et
3 autres coeurs intacts sur toutes les captures fournies). L'ancien seuil
(0.85, ~21.25% sur 4 coeurs) se declenchait donc systematiquement sur du
fonctionnement SAIN a partir du niveau Moyen, jamais sur un vrai risque —
d'ou aussi l'exigence conjointe de GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_
PERCENT ci-dessous (le generateur ne doit plus jamais arreter un test a
lui seul, seulement si la MACHINE ENTIERE est egalement sous pression)."""

GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_PERCENT: float = 90.0
"""Condition AJOUTEE le 2026-09-01 (bug reel, meme session que la
correction ci-dessus) : le CPU generateur seul, meme au ratio releve
ci-dessus, ne suffit plus a arreter un test — le CPU GLOBAL de la machine
(cpu_percent_global, deja mesure sur chaque SystemSnapshot mais jusqu'ici
jamais consulte par ce garde-fou) doit ETRE AUSSI sature en meme temps
(voir evaluate_generator_resources() : les deux conditions sont exigees
CONJOINTEMENT — ET, jamais OU). Raison : le generateur (moteur asyncio
lie au GIL) sature NORMALEMENT et SANS DANGER son seul coeur exploitable
des qu'un test Connexions atteint un niveau moyen/eleve, meme si les
coeurs restants et la memoire de la machine restent totalement
disponibles (confirme par toutes les captures d'ecran du bug rapporte :
CPU 40%, plusieurs Go de RAM libres). Un vrai risque pour L'HOTE
lui-meme (et non pour la seule mesure du test) suppose que la machine
DANS SON ENSEMBLE soit sous pression, pas seulement le coeur que le
generateur utilise deja normalement. Meme valeur (90%) et meme principe
que domain/calibration/policies.py::CALIBRATION_STOP_CPU_GLOBAL_MIN_
PERCENT, deja construit ainsi des le depart pour le calibrage — jamais
retro-applique aux runs reels avant ce correctif."""

GENERATOR_CPU_ABORT_SUSTAINED_SAMPLES: int = 3
"""Nombre d'echantillons CONSECUTIFS (1s chacun, SAMPLE_INTERVAL_SECONDS)
qui doivent TOUS depasser le seuil derive de
GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE avant abort — jamais un seul
pic isole."""

MEMORY_AVAILABLE_ABORT_THRESHOLD_PERCENT: float = 15.0
"""Document : "Memoire disponible" palier Abort (<=15%)."""

OPEN_FILES_ABORT_RATIO: float = 0.75
"""Document : "FDs du processus" palier Abort (>=75% de la limite
douce, domain/runs/models.py::SystemSnapshot.open_files_soft_limit)."""

GENERATOR_MAX_CONCURRENT_REQUESTS_PER_INTERVAL: int = 200
"""Plafond technique (pas issu du document produit, choix operationnel
propre a cette implementation — meme statut que MINIMUM_OPEN_FILES_SOFT_
LIMIT ci-dessus) sur le nombre de requetes REELLEMENT en vol en meme
temps au sein d'UN intervalle d'1s (infrastructure/runner/
httpx_load_generator.py::_run_interval(), via asyncio.Semaphore) — les
requetes EXCEDENTAIRES de l'intervalle attendent leur tour plutot que
d'etre toutes lancees d'un bloc.

Bug reel rapporte (2026-09-01, session de test utilisateur, captures
d'ecran) sur Test connexions Agressif/Haut et Test requetes Maximum :
interface TUI gelee, latence rapportee depassant le timeout httpx
configure (10s) sans qu'aucune erreur ne soit comptee, arrets CPU
generateur au bout de 3s alors que l'utilisation systeme observee restait
faible, et un compteur de test manuel non reproductible (parfois termine
normalement, parfois arrete a 3s pour la MEME configuration). Avant ce
correctif, _run_interval() lancait `request_count` taches asyncio.gather()
d'un seul coup CHAQUE SECONDE — jusqu'a 5000 pour Test connexions Maximum
— sans aucune limite hormis le pool de connexions httpx lui-meme
(_MAX_CONCURRENT_CONNECTIONS). Mesure empirique en session (serveur de
boucle locale du calibrage, machine de developpement) : une seule salve
de 200 requetes concurrentes prend deja ~1.8s reel (au-dela du budget
d'1s par intervalle), une salve de plusieurs milliers prendrait donc
plusieurs dizaines de secondes — pendant lesquelles `_run_interval()`
reste bloque sur un unique `await asyncio.gather(...)`, gelant toute la
boucle asyncio partagee avec l'interface Textual (aucun processus/thread
separe, voir httpx_load_generator.py INFO DEV), retardant d'autant la
publication de l'echantillon suivant (d'ou le compteur de progression qui
derive du temps reel) et empechant les guards (application/pipeline/
guards/resource_guard.py) de reagir avant la fin de la salve entiere.

Valeur choisie (200) : egale au preset "Haut" (domain/load/presets.py),
volontairement CONSERVATRICE — aucun niveau Faible a Haut n'est donc
throttle par ce plafond (comportement inchange), seuls Puissant/Agressif/
Violent/Maximum (qui depassent deja 200 en concurrence ou en requetes/s)
sont desormais debites par lots plutot qu'en une seule salve massive.
Meme principe deja applique correctement des sa premiere version a
infrastructure/calibration/stage_runner.py (asyncio.Semaphore(vu_target)),
jamais retro-applique au generateur reel avant ce correctif."""

SAFETY_MODE_DESCRIPTION: str = (
    "Le mode securite (actif par defaut) arrete automatiquement un test "
    "si CETTE machine - pas la cible testee - semble en danger (CPU/"
    "memoire du generateur). Le desactiver ne change rien aux "
    "protections de la cible (taux d'erreur, latence : toujours "
    "actives) : seul le risque de ralentir ou geler temporairement "
    "VOTRE ordinateur pendant la duree du test augmente, surtout sur "
    "les niveaux intensifs (Connexions Agressif et au-dela, Requetes "
    "Maximum). A desactiver si vous savez que votre machine peut "
    "encaisser plus que ce que le mode securite suppose par defaut."
)
"""Texte explicatif UNIQUE (2026-09-01, "mode securite" a cocher au
lancement, bug reel rapporte avec captures d'ecran) — reutilise tel quel
par interfaces/cli/commands/run_command.py (--help) et les 3 ecrans de
lancement TUI, jamais deux formulations qui pourraient diverger sur un
sujet aussi sensible (meme principe que domain/reports/builders.py::
VERDICT_HEADLINES). Decrit ce que bascule LoadPlan.safety_mode (domain/
load/models.py) : uniquement application/pipeline/guards/resource_
guard.py, jamais threshold_guard.py (protection de la cible, toujours
active)."""

# --- Profils de duree nommes D1-D6 (mode "profil") — source produit :
# omega-stress-calibrage-profils-securite.md, section "Durees verrouillees".

REINFORCED_CONFIRMATION_PHRASE: str = "JE_CONFIRME_LA_CIBLE_AUTORISEE"
"""Texte exact exige pour lancer un run au niveau `reinforced_level` d'un
profil de duree (domain/load/duration_presets.py::DurationPreset) — voir
domain/load/validators.py::evaluate_duration_preset(). Citee telle quelle
dans le document, section "confirmation renforcee"."""


def allowed_durations_minutes(
    level: IntensityLevel, *, extended_authorized: bool = False
) -> tuple[int, ...]:
    """Durees autorisees (en minutes) pour un niveau d'intensite donne —
    3 paliers :

    - jamais gate (level ni dans PRECHECK_OPTIONAL_LEVELS ni dans
      PRECHECK_MANDATORY_LEVELS) : toutes les durees ALWAYS_AVAILABLE,
      sans condition ;
    - gate OBLIGATOIRE (PRECHECK_MANDATORY_LEVELS) : toujours
      GATED_BASE_DURATIONS_MINUTES seulement — extended_authorized est
      ignore ici, le pre-check conditionne l'acces au niveau lui-meme
      (voir application/pipeline/guards/precheck_guard.py), pas une duree
      etendue ;
    - gate OPTIONNEL (PRECHECK_OPTIONAL_LEVELS) : GATED_BASE_DURATIONS_MINUTES,
      plus GATED_EXTENDED_DURATIONS_MINUTES si extended_authorized reflete
      une autorisation deja acquise (profil fige l'autorisant explicitement,
      ou pre-check valide).

    Ce n'est jamais une saisie libre : toujours un sous-ensemble des
    valeurs figees ci-dessus.
    """
    if level in PRECHECK_MANDATORY_LEVELS:
        return GATED_BASE_DURATIONS_MINUTES
    if level in PRECHECK_OPTIONAL_LEVELS:
        if extended_authorized:
            return (*GATED_BASE_DURATIONS_MINUTES, *GATED_EXTENDED_DURATIONS_MINUTES)
        return GATED_BASE_DURATIONS_MINUTES
    return ALWAYS_AVAILABLE_DURATIONS_MINUTES


def is_precheck_mandatory(level: IntensityLevel) -> bool:
    """True si le niveau exige un pre-check automatique et obligatoire."""
    return level in PRECHECK_MANDATORY_LEVELS


def is_precheck_optional(level: IntensityLevel) -> bool:
    """True si le niveau propose un pre-check FACULTATIF (deverrouille
    GATED_EXTENDED_DURATIONS_MINUTES, sans jamais bloquer le demarrage —
    voir is_precheck_mandatory() pour le palier oppose)."""
    return level in PRECHECK_OPTIONAL_LEVELS


def is_precheck_available(level: IntensityLevel) -> bool:
    """True si un pre-check peut etre propose pour ce niveau (obligatoire
    OU facultatif) — distinct de is_precheck_mandatory() : un niveau gate
    optionnel (Puissant/Agressif) doit pouvoir proposer le pre-check dans
    l'UI sans pour autant l'exiger pour demarrer (voir interfaces/tui/
    screens/*_panel.py, cadre #precheck-frame)."""
    return is_precheck_mandatory(level) or is_precheck_optional(level)

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
# - Modele pre-check/duree a 3 paliers (2026-09-01) : jamais gate
#   (Faible/Bas/Moyen-Normal/Haut-Fort) / gate optionnel (Puissant/
#   Agressif, PRECHECK_OPTIONAL_LEVELS) / gate obligatoire (Violent/
#   Maximum, PRECHECK_MANDATORY_LEVELS) — remplace l'ancien modele binaire
#   (2 paliers). is_precheck_mandatory() reste la seule condition qui bloque
#   validate_plan() (PrecheckRequiredError) ; is_precheck_available() est un
#   AJOUT distinct pour l'affichage UI uniquement (propose le pre-check sans
#   l'exiger sur le palier optionnel), ne doit jamais etre confondue avec
#   is_precheck_mandatory() dans une regle de validation.
# Comment il sera utilise (apercu) :
# - domain/load/validators.py (plan_validator, threshold_evaluator)
#   appellera allowed_durations_minutes() pour rejeter une duree hors
#   bornes.
# - application/pipeline/guards/precheck_guard.py appellera
#   is_precheck_mandatory() avant d'autoriser un lancement Violent/Maximum.
# - infrastructure/runner/async_worker.py publiera la progression au rythme
#   de SAMPLE_INTERVAL_SECONDS via le port run_progress_notifier.
# - application/pipeline/degraded_mode.py et domain/reports/builders.py
#   consomment tous deux LOCAL_BOTTLENECK_RATIO_THRESHOLD.
# - infrastructure/probe/local_probe.py consomme MINIMUM_VIABLE_CPU_COUNT,
#   MINIMUM_VIABLE_RAM_MB et MINIMUM_OPEN_FILES_SOFT_LIMIT pour classer les
#   Capability qu'il produit (jamais de seuil chiffre code en dur cote
#   infrastructure).
#---------------------------------------------------------------------->
