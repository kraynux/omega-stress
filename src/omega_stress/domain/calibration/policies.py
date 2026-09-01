# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Politiques de bornage du sous-domaine calibration : paliers, marge de
securite, preconditions, criteres sante/arret.

Source produit : omega-stress-calibrage-profils-securite.md, sections
"Calibrage unique et persistant" (tables "Preconditions du calibrage",
"Deroule de calibrage", "Passage ou arret"). Toute valeur ici modifiee
doit l'etre en accord avec ce document — voir ARCHITECTURE.md §2 (regle
de placement des politiques) et §11 (revue de PR : aucune valeur de
seuil/duree en dehors de ce fichier).
"""
from __future__ import annotations

from omega_stress.domain.calibration.models import CalibrationStage

CALIBRATION_STAGES: tuple[CalibrationStage, ...] = (
    CalibrationStage(
        id="idle_baseline", name="Reference a vide",
        vu_target=0, rps_target=0, window_seconds=5, conditional=False,
    ),
    CalibrationStage(
        id="calib_1", name="Palier 1", vu_target=25, rps_target=100,
        window_seconds=10, conditional=False,
    ),
    CalibrationStage(
        id="calib_2", name="Palier 2", vu_target=100, rps_target=500,
        window_seconds=10, conditional=False,
    ),
    CalibrationStage(
        id="calib_3", name="Palier 3", vu_target=250, rps_target=1500,
        window_seconds=15, conditional=False,
    ),
    CalibrationStage(
        id="calib_4", name="Palier 4", vu_target=500, rps_target=3000,
        window_seconds=15, conditional=False,
    ),
    CalibrationStage(
        id="calib_5", name="Palier 5 (conditionnel)", vu_target=1000,
        rps_target=6000, window_seconds=20, conditional=True,
    ),
    CalibrationStage(
        id="calib_6", name="Palier 6 (conditionnel)", vu_target=2000,
        rps_target=12000, window_seconds=20, conditional=True,
    ),
)
"""Les 7 paliers de progression, dans l'ordre d'execution. Paliers 5/6
(conditional=True) ne sont executes QUE si le palier precedent est sain
(voir application/commands/run_calibration.py)."""

CALIBRATION_SAFETY_MARGIN: float = 0.70
"""Marge appliquee au dernier palier sain pour obtenir VU_safe/RPS_safe
(document : "laisse environ 30% de reserve afin de preserver la machine
hote... et les variations entre le calibrage local et un test reel
distant")."""

CALIBRATION_TARGET_PATH: str = "/__omega_calibration__/payload-4k"
"""Document, table "Cible de calibrage" : chemin fixe du serveur de
boucle locale integre a Omega-Stress. Constante de policy (pas un detail
d'infrastructure) : partagee entre infrastructure/calibration/
local_server.py (la sert) et infrastructure/calibration/stage_runner.py
(la requete) — une seule source, jamais deux chaines qui pourraient
diverger."""

CALIBRATION_PAYLOAD_SIZE_BYTES: int = 4096
"""Document, meme table : "Reponse : 4 KiB fixe et deterministe"."""

CALIBRATION_PRECONDITION_CPU_GLOBAL_MAX_PERCENT: float = 70.0
"""Document, table "Preconditions du calibrage" : CPU global moyen sur 5
secondes, refuse si depasse. Valeur documentee a l'origine (35.0) relevee
a 70.0 le 2026-09-01 (demande explicite, bug reel rapporte en session) :
35% refusait de DEMARRER un calibrage sur une machine de bureau normale
avec de l'activite en arriere-plan (confirme en session : calibrage
refuse/interrompu alors que l'utilisateur observait 9% CPU sur son
propre moniteur systeme) — "sur un gros processeur [70%] c'est nettement
suffisant" comme marge avant de commencer a mesurer. Coherent avec
GENERATOR_CPU_ABORT_GLOBAL_THRESHOLD_PERCENT/CALIBRATION_STOP_CPU_
GLOBAL_MIN_PERCENT (tous deux 90.0, meme session) : cette precondition
reste volontairement plus basse (70 < 90), un vrai MARGIN avant de
commencer, pas le seuil de danger lui-meme."""

CALIBRATION_PRECONDITION_MEMORY_AVAILABLE_MIN_PERCENT: float = 20.0
"""Document, meme table : memoire disponible, refuse si en dessous."""

CALIBRATION_HEALTHY_CPU_GLOBAL_MAX_PERCENT: float = 85.0
"""Document, table "Passage ou arret", condition de palier sain : CPU
global."""

CALIBRATION_HEALTHY_CPU_GENERATOR_MAX_RATIO_OF_SINGLE_CORE: float = 0.90
"""Document : "CPU Omega-Stress < 80%" — deja exprime relatif a ce qu'UN
SEUL coeur logique peut fournir (100 / nombre de coeurs), jamais un
pourcentage absolu fixe. Meme correction que domain/load/policies.py::
GENERATOR_CPU_WARNING_THRESHOLD/GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE
(bug reel corrige le 2026-09-01 sur le mecanisme de guard live, applique
ici directement plutot que de repeter la meme erreur) : un moteur
asyncio lie au GIL ne peut saturer qu'un seul coeur, quel que soit le
nombre de coeurs disponibles par ailleurs.

Releve de 0.80 a 0.90 le 2026-09-01 (meme jour, second correctif suite a
une nouvelle session de calibrage utilisateur toujours en echec des le
palier 1 : "je suis entre 8 et 21%") : meme diagnostic empirique que
domain/load/policies.py::GENERATOR_CPU_ABORT_RATIO_OF_SINGLE_CORE (voir
son propre commentaire) — un test meme leger sature legitimement 20-25%
d'un coeur normalise sur une machine a 4 coeurs, jamais un signe de
danger en soi. Voir aussi evaluate_stage_outcome() : le critere d'ARRET
exige desormais AUSSI CALIBRATION_STOP_CPU_GLOBAL_MIN_PERCENT (ET, plus
OU) — meme principe que domain/load/validators.py::
evaluate_generator_resources()."""

CALIBRATION_HEALTHY_MEMORY_AVAILABLE_MIN_PERCENT: float = 20.0
"""Document, meme table : memoire disponible pendant le palier."""

CALIBRATION_HEALTHY_ERROR_RATE_MAX: float = 0.005
"""Document : "Erreurs locales < 0,5%"."""

CALIBRATION_HEALTHY_RPS_ACHIEVED_RATIO_MIN: float = 0.85
"""Document : "RPS reel >= 85% du RPS cible, ou progression nette
coherente" — seule la premiere moitie (ratio fixe) est retenue ici, la
"progression nette coherente" reste qualitative et non chiffree par le
document, non implementee (angle mort assume, voir plan)."""

CALIBRATION_STOP_CPU_GENERATOR_MIN_RATIO_OF_SINGLE_CORE: float = 0.95
"""Document : "CPU Omega-Stress >= 85%" — meme correction relative au
coeur unique que CALIBRATION_HEALTHY_CPU_GENERATOR_MAX_RATIO_OF_SINGLE_CORE
ci-dessus. Releve de 0.85 a 0.95 le 2026-09-01, meme raison et meme
session que cette derniere — desormais NECESSAIRE MAIS PAS SUFFISANT a
lui seul pour arreter un palier : evaluate_stage_outcome() exige aussi
CALIBRATION_STOP_CPU_GLOBAL_MIN_PERCENT sature EN MEME TEMPS (ET, jamais
OU comme avant ce correctif) — un palier ne doit plus jamais s'arreter
sur le seul CPU du generateur (saturation normale d'un coeur), seulement
si la machine ENTIERE est aussi sous pression."""

CALIBRATION_STOP_SUSTAINED_SECONDS: int = 3
"""Document : "pendant au moins 3 secondes" — s'applique aux deux
criteres CPU (generateur et global) ci-dessous."""

CALIBRATION_STOP_CPU_GLOBAL_MIN_PERCENT: float = 90.0
"""Document : "CPU global >= 90% pendant au moins 3 secondes"."""

CALIBRATION_STOP_MEMORY_AVAILABLE_MAX_PERCENT: float = 15.0
"""Document : "Memoire disponible <= 15%"."""

CALIBRATION_STOP_ERROR_RATE_MIN: float = 0.01
"""Document : "Erreurs locales >= 1% sur une fenetre stable"."""

CALIBRATION_STOP_CONSECUTIVE_TIMEOUTS: int = 50
"""Document : "50 timeouts consecutifs vers le serveur local de
calibrage"."""

CALIBRATION_STOP_RPS_ACHIEVED_RATIO_MAX: float = 0.85
"""Document : "RPS reel < 85% du RPS cible sur deux paliers consecutifs"
— seuil du ratio ; voir CALIBRATION_STOP_RPS_ACHIEVED_CONSECUTIVE_STAGES
pour le nombre de paliers consecutifs requis."""

CALIBRATION_STOP_RPS_ACHIEVED_CONSECUTIVE_STAGES: int = 2
"""Document, meme phrase : nombre de paliers CONSECUTIFS sous
CALIBRATION_STOP_RPS_ACHIEVED_RATIO_MAX avant arret."""

CALIBRATION_VALIDITY_DAYS_RECOMMENDED: int = 30
"""Document : "il est recommande de le renouveler apres 30 jours" —
metadonnee affichee (age du calibrage), aucune notification proactive
construite dans ce premier chantier (voir plan, "Angles morts")."""

CALIBRATION_VALIDITY_DAYS_MANDATORY: int = 90
"""Document : "obligatoire apres 90 jours" — meme statut que
CALIBRATION_VALIDITY_DAYS_RECOMMENDED, affichage seul en V1, aucun
blocage applicatif construit ici."""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte toutes les valeurs numeriques du sous-domaine calibration :
#   definition des 7 paliers, marge de securite, seuils de precondition/
#   sante/arret, duree de validite.
# Pourquoi dans domain/calibration/ (charte) :
# - Meme raisonnement que domain/load/policies.py : politiques de
#   securite/produit au sens strict d'ARCHITECTURE.md §2, figurent sous
#   forme de table dans le document produit.
# Ce qu'il ne contient PAS :
# - Aucune logique d'evaluation (voir domain/calibration/validators.py,
#   qui consomme ces constantes plutot que de les redefinir).
# - Aucun sondage systeme (voir infrastructure/calibration/).
# Points cles :
# - Les deux seuils CPU generateur (sante et arret) sont deliberement
#   exprimes en RATIO D'UN SEUL COEUR des leur introduction, jamais en
#   pourcentage absolu — contrairement a domain/load/policies.py::
#   GENERATOR_CPU_ABORT_THRESHOLD qui a du etre corrige apres coup
#   (bug reel, 2026-09-01, meme session). La NORMALISATION par coeur
#   n'a donc jamais eu besoin d'etre corrigee ici — mais les VALEURS
#   exactes des ratios (0.80/0.85 a l'origine) se sont quand meme
#   averees trop basses en pratique (calibrage systematiquement en echec
#   des le palier 1, meme sur une machine peu chargee) et ont du etre
#   relevees a 0.90/0.95 le meme jour, avec un critere d'ARRET desormais
#   ET (generateur + global ensemble) plutot que OU — voir validators.py.
# - CALIBRATION_STAGES est un tuple de dataclasses deja construites
#   (pas de dict indexe par id) : l'ordre de declaration EST l'ordre
#   d'execution, jamais reordonne par un tri implicite.
# Comment il sera utilise (apercu) :
# - domain/calibration/validators.py consomme toutes ces constantes.
# - application/commands/run_calibration.py itere CALIBRATION_STAGES
#   dans l'ordre, s'arretant ou sautant les paliers conditionnels selon
#   les verdicts de validators.py.
#---------------------------------------------------------------------->
