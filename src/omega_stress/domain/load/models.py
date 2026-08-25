# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entites et value objects du sous-domaine load : seuils, duree, etapes de rampe, plan."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import ValidationError
from omega_stress.domain.load import policies


@dataclass(frozen=True, slots=True)
class Thresholds:
    """Seuils d'arret automatique d'un run. Jamais saisis librement par
    l'utilisateur (voir plan produit, "Panneau de tests") : toujours issus
    d'un profil fige ou d'un resultat de pre-check."""

    max_error_rate: float
    max_p95_latency_ms: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.max_error_rate <= 1.0:
            raise ValidationError(
                f"max_error_rate doit etre compris entre 0.0 et 1.0, recu {self.max_error_rate!r}"
            )
        if self.max_p95_latency_ms is not None and self.max_p95_latency_ms <= 0:
            raise ValidationError(
                f"max_p95_latency_ms doit etre strictement positif, "
                f"recu {self.max_p95_latency_ms!r}"
            )


@dataclass(frozen=True, slots=True)
class Duration:
    """Duree totale d'un run, toujours issue d'un choix ferme de
    domain/load/policies.py — jamais une valeur arbitraire."""

    minutes: int

    @staticmethod
    def for_level(
        level: IntensityLevel, minutes: int, *, extended_authorized: bool = False
    ) -> Result[Duration, ValidationError]:
        """Constructeur intelligent : refuse toute duree hors des choix
        fermes pour le niveau donne plutot que de laisser construire une
        Duration invalide silencieusement."""
        allowed = policies.allowed_durations_minutes(level, extended_authorized=extended_authorized)
        if minutes not in allowed:
            return Err(
                ValidationError(
                    f"Duree {minutes} min non autorisee pour le niveau {level.value} "
                    f"(choix fermes : {allowed})"
                )
            )
        return Ok(Duration(minutes=minutes))


@dataclass(frozen=True, slots=True)
class RampStep:
    """Etape de montee progressive, exprimee en fraction de l'intensite de
    pic (0.0-1.0) plutot qu'en valeur absolue : la valeur absolue (req/min
    ou connexions) est resolue au moment de l'execution a partir du
    RampPreset du niveau choisi (domain/load/presets.py), pour ne pas
    dupliquer la distinction Test requetes / Test connexions dans l'etape
    elle-meme."""

    order: int
    duration_minutes: float
    start_ratio: float
    end_ratio: float

    def __post_init__(self) -> None:
        for field_name, value in (("start_ratio", self.start_ratio), ("end_ratio", self.end_ratio)):
            if not 0.0 <= value <= 1.0:
                raise ValidationError(
                    f"{field_name} doit etre compris entre 0.0 et 1.0, recu {value!r}"
                )
        if self.duration_minutes <= 0:
            raise ValidationError(
                f"duration_minutes doit etre strictement positif, recu {self.duration_minutes!r}"
            )


@dataclass(frozen=True, slots=True)
class LoadPlan:
    """Plan de test fige, pret a etre execute par le pipeline
    (application/pipeline/). Sa validite structurelle est verifiee par
    domain/load/validators.py::validate_plan avant tout lancement."""

    id: str
    family: TestFamily
    level: IntensityLevel
    duration: Duration
    thresholds: Thresholds
    target_authorization_confirmed: bool
    precheck_validated: bool = False
    ramp_steps: tuple[RampStep, ...] = ()
    notes: str = ""

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte les entites/value objects centraux du sous-domaine load :
#   Thresholds (seuils d'arret), Duration (constructeur intelligent borne
#   par policies.py), RampStep (etape de rampe en ratio), LoadPlan
#   (assemblage final soumis a validation avant execution).
# Pourquoi dans domain/load/ (charte) :
# - Entites/VO metier pures, aucune I/O, aucune dependance a Textual/httpx/
#   sqlite3. Duration.for_level() consomme domain/load/policies.py (meme
#   sous-domaine), pas une regle dupliquee ici.
# Ce qu'il ne contient PAS :
# - Aucune validation de plan complet (coherence family/ramp_steps,
#   autorisation cible, pre-check) : voir domain/load/validators.py.
# - Aucune construction concrete de RampStep a partir d'un preset : voir
#   domain/load/builders.py.
# - Aucune valeur numerique de charge (req/min, connexions) : voir
#   domain/load/presets.py, consomme par builders.py au moment de la
#   resolution.
# Points cles :
# - Thresholds et RampStep valident leurs invariants directement dans
#   __post_init__ (levee immediate de ValidationError) : ce sont des
#   invariants de construction, pas des echecs metier attendus d'un
#   parcours utilisateur normal (les seuils/ratios ne sont jamais saisis
#   librement, voir policies.py et le plan produit).
# - Duration.for_level() est le seul point d'entree recommande pour
#   construire une Duration a partir d'une saisie utilisateur ; le
#   constructeur brut Duration(minutes=x) reste possible (ex. reconstruction
#   depuis un repository) mais n'est pas revalide ici — c'est le role de
#   domain/load/validators.py::validate_plan au moment de valider un
#   LoadPlan complet.
# Comment il sera utilise (apercu) :
# - domain/load/builders.py construit des RampStep a partir des presets.
# - domain/load/validators.py consomme LoadPlan/Thresholds pour valider un
#   plan et evaluer un seuil pendant l'execution.
# - domain/profiles/models.py reutilise Duration et Thresholds tels quels.
#---------------------------------------------------------------------->
