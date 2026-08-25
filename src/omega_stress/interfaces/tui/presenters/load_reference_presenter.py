# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : tableau de reperes (debit/connexions/durees reels) par
type de test et niveau, pour l'ecran Aide."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import IntensityLevel, TestFamily
from omega_stress.domain.load.policies import allowed_durations_minutes, is_precheck_mandatory
from omega_stress.domain.load.presets import fixed_rate_preset, ramp_preset


@dataclass(frozen=True, slots=True)
class LoadReferenceRow:
    """Une ligne du tableau (type de test x niveau)."""

    test_type: str
    level: str
    dimension: str
    target: str
    burst: str
    precheck: str
    durations: str


def _burst_per_second(requests_per_minute: int) -> int:
    return round(requests_per_minute / 60)


def _duration_label(level: IntensityLevel) -> str:
    """Libelle des durees disponibles pour ce niveau — derive UNIQUEMENT
    de domain/load/policies.py::allowed_durations_minutes() (jamais de
    valeur en dur ici), pour rester automatiquement a jour si ces regles
    changent."""
    default = allowed_durations_minutes(level)
    if not is_precheck_mandatory(level):
        return f"{default[0]} a {default[-1]} min"
    extended = allowed_durations_minutes(level, extended_authorized=True)
    extra = [m for m in extended if m not in default]
    default_text = " ou ".join(f"{m} min" for m in default)
    if not extra:
        return default_text
    extra_text = " ou ".join(f"{m} min" for m in extra)
    return f"{default_text} ({extra_text} si pre-check)"


def _precheck_label(level: IntensityLevel) -> str:
    return "Oui" if is_precheck_mandatory(level) else "Non"


def load_reference_rows() -> tuple[LoadReferenceRow, ...]:
    """Une ligne par (famille de test, niveau), dans l'ordre d'affichage
    voulu (une famille a la fois, niveaux du plus bas au plus haut).
    Toutes les valeurs viennent de domain/load/presets.py et policies.py
    (aucune valeur de charge/duree en dur dans ce fichier, voir
    ARCHITECTURE.md §11) : ce presenter ne fait que mettre en forme des
    chiffres deja figes ailleurs, jamais en inventer un nouveau."""
    rows: list[LoadReferenceRow] = []

    for level in IntensityLevel:
        preset = fixed_rate_preset(level)
        rows.append(
            LoadReferenceRow(
                test_type="Test requetes",
                level=level.value.capitalize(),
                dimension="Debit",
                target=f"{preset.requests_per_minute} req/min",
                burst=f"~{_burst_per_second(preset.requests_per_minute)} req/s en rafale",
                precheck=_precheck_label(level),
                durations=_duration_label(level),
            )
        )

    for level in IntensityLevel:
        preset = fixed_rate_preset(level)
        rows.append(
            LoadReferenceRow(
                test_type="Test connexions",
                level=level.value.capitalize(),
                dimension="Connexions simultanees",
                target=f"{preset.concurrent_connections} connexions",
                burst=f"{preset.concurrent_connections} en parallele, chaque seconde",
                precheck=_precheck_label(level),
                durations=_duration_label(level),
            )
        )

    for level in IntensityLevel:
        ramp = ramp_preset(level)
        rows.append(
            LoadReferenceRow(
                test_type="Test charge",
                level=level.value.capitalize(),
                dimension="Debit (montee puis plateau)",
                target=f"pic {ramp.peak_requests_per_minute} req/min",
                burst=(
                    f"rampe {ramp.ramp_up_minutes:g} min "
                    f"-> plateau {ramp.plateau_minutes_min:g} min"
                ),
                precheck=_precheck_label(level),
                durations=_duration_label(level),
            )
        )

    return tuple(rows)


def load_reference_family_note(family: TestFamily) -> str:
    """Rappel textuel de la dimension reellement pilotee par cette
    famille — evite qu'un utilisateur suppose que le second nombre du
    preset (ex. connexions pour Test requetes) joue un role qu'il n'a
    pas dans cette famille precise (voir infrastructure/runner/
    engine_params.py::target_for_interval, seule source de verite)."""
    if family is TestFamily.REQUEST:
        return "Seul le debit (req/min) pilote ce test ; la simultaneite en decoule."
    if family is TestFamily.CONNECTION:
        return "Seule la simultaneite (connexions) pilote ce test ; aucun debit cible."
    return (
        "Seul le debit au pic pilote ce test, atteint progressivement : sur une duree "
        "choisie plus courte que la rampe indiquee, le pic n'est jamais atteint."
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Traduit domain/load/presets.py + policies.py en lignes de tableau
#   directement affichables (widgets/load_reference_table.py), pour
#   repondre au besoin utilisateur "controler les metriques par type de
#   test et leur niveau... j'ai un doute [sur ce que veut dire une cible
#   de charge]".
# Pourquoi dans interfaces/tui/presenters/ (charte) :
# - Lit domain/load/ en lecture seule, ne construit ni n'execute jamais
#   de LoadPlan : un presenter de mise en forme pure, meme role que
#   theme_presenter.py/run_presenter.py pour leurs domaines respectifs.
# Ce qu'il ne contient PAS :
# - Aucune valeur numerique en dur : chaque nombre affiche vient d'un
#   appel a fixed_rate_preset()/ramp_preset()/allowed_durations_minutes()/
#   is_precheck_mandatory() — si ces politiques changent, ce presenter
#   suit automatiquement sans modification.
# - Aucune mention du plafond de connexions httpx (infrastructure/
#   runner/httpx_load_generator.py::_MAX_CONCURRENT_CONNECTIONS) : ce
#   presenter documente la POLITIQUE de charge (domain/), pas un detail
#   d'implementation du runner (infrastructure/) — un contrat
#   import-linter interdirait de toute facon a interfaces/ d'importer
#   infrastructure/ directement (voir pyproject.toml).
# Points cles :
# - _burst_per_second() arrondit requests_per_minute/60 : c'est
#   EXACTEMENT le calcul fait par infrastructure/runner/engine_params.py
#   pour la rafale reelle par intervalle d'1 seconde (SAMPLE_INTERVAL_
#   SECONDS) — duplique ici volontairement en une ligne simple plutot que
#   d'importer infrastructure/ depuis interfaces/ (interdit, voir
#   ci-dessus) pour une seule formule triviale.
# - _duration_label() : "(X min si pre-check)" seulement si extended_
#   authorized ajoute reellement une duree supplementaire par rapport au
#   defaut — jamais suppose que c'est toujours "5 min" (deriverait de
#   GATED_EXTENDED_DURATION_MINUTES sans le nommer en dur ici).
# - load_reference_family_note() : rappel qualitatif complementaire au
#   tableau chiffre, pour eviter la confusion notee par l'utilisateur
#   entre les deux dimensions d'un meme FixedRatePreset/RampPreset
#   (ex. Test requetes n'utilise jamais concurrent_connections, Test
#   charge n'utilise jamais peak_connections — voir engine_params.py).
# Comment il sera utilise :
# - interfaces/tui/widgets/load_reference_table.py (DataTable),
#   interfaces/tui/screens/help_screen.py (section "Reperes de charge").
#---------------------------------------------------------------------->
