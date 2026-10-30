# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Presenter : tableau de reperes (debit/connexions/durees reels) par
type de test et niveau, pour l'ecran Aide."""
from __future__ import annotations

from dataclasses import dataclass

from omega_stress.core.enums import DurationPresetId, IntensityLevel, TestFamily
from omega_stress.domain.load.duration_presets import DURATION_PRESETS
from omega_stress.domain.load.policies import (
    allowed_durations_minutes,
    is_precheck_mandatory,
    is_precheck_optional,
)
from omega_stress.domain.load.presets import fixed_rate_preset, ramp_preset
from omega_stress.shared.i18n import _


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


@dataclass(frozen=True, slots=True)
class DurationPresetReferenceRow:
    """Une ligne du tableau des profils de duree D1-D6 (mode "profil")."""

    id: str
    name: str
    total_minutes: int
    families: str
    free_levels: str
    reinforced_level: str


def _burst_per_second(requests_per_minute: int) -> int:
    return round(requests_per_minute / 60)


def _duration_label(level: IntensityLevel) -> str:
    """Libelle des durees disponibles pour ce niveau — derive UNIQUEMENT
    de domain/load/policies.py::allowed_durations_minutes() (jamais de
    valeur en dur ici), pour rester automatiquement a jour si ces regles
    changent. 3 paliers (Phase 3, 2026-09-01) : jamais gate (fourchette
    continue) / gate obligatoire (durees de base fermes, le pre-check ne
    les etend jamais) / gate optionnel (durees de base + extension
    mentionnee seulement si le pre-check en debloque reellement)."""
    default = allowed_durations_minutes(level)
    if not is_precheck_mandatory(level) and not is_precheck_optional(level):
        return _("{value} à {value2} min").format(value=default[0], value2=default[-1])
    default_text = " ou ".join(f"{m} min" for m in default)
    if is_precheck_mandatory(level):
        return default_text
    extended = allowed_durations_minutes(level, extended_authorized=True)
    extra = [m for m in extended if m not in default]
    if not extra:
        return default_text
    extra_text = " ou ".join(f"{m} min" for m in extra)
    return _("{default_text} ({extra_text} si pré-check)").format(
        default_text=default_text, extra_text=extra_text
    )


def _precheck_label(level: IntensityLevel) -> str:
    if is_precheck_mandatory(level):
        return _("Oui")
    if is_precheck_optional(level):
        return _("Non/Oui")
    return _("Non")


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
                test_type=_("Test requêtes"),
                level=level.value.capitalize(),
                dimension=_("Débit"),
                target=_("{requests_per_minute} req/min").format(
                    requests_per_minute=preset.requests_per_minute
                ),
                burst=_("~{value} req/s en rafale").format(
                    value=_burst_per_second(preset.requests_per_minute)
                ),
                precheck=_precheck_label(level),
                durations=_duration_label(level),
            )
        )

    for level in IntensityLevel:
        preset = fixed_rate_preset(level)
        rows.append(
            LoadReferenceRow(
                test_type=_("Test connexions"),
                level=level.value.capitalize(),
                dimension=_("Connexions simultanées"),
                target=_("{concurrent_connections} connexions").format(
                    concurrent_connections=preset.concurrent_connections
                ),
                burst=_("{concurrent_connections} en parallèle, chaque seconde").format(
                    concurrent_connections=preset.concurrent_connections
                ),
                precheck=_precheck_label(level),
                durations=_duration_label(level),
            )
        )

    for level in IntensityLevel:
        ramp = ramp_preset(level)
        rows.append(
            LoadReferenceRow(
                test_type=_("Test charge"),
                level=level.value.capitalize(),
                dimension=_("Débit (montée puis plateau)"),
                target=_("pic {peak_requests_per_minute} req/min").format(
                    peak_requests_per_minute=ramp.peak_requests_per_minute
                ),
                burst=(
                    _(
                        "rampe {ramp_up_minutes:g} min -> plateau {plateau_minutes_min:g} min"
                    ).format(
                        ramp_up_minutes=ramp.ramp_up_minutes,
                        plateau_minutes_min=ramp.plateau_minutes_min,
                    )
                ),
                precheck=_precheck_label(level),
                durations=_duration_label(level),
            )
        )

    return tuple(rows)


_FAMILY_LABELS: dict[TestFamily, str] = {
    TestFamily.REQUEST: _("Requêtes"),
    TestFamily.CONNECTION: _("Connexions"),
    TestFamily.RAMP: _("Charge"),
}


def duration_preset_reference_rows() -> tuple[DurationPresetReferenceRow, ...]:
    """Une ligne par profil de duree D1-D6 (domain/load/duration_presets.py
    ::DURATION_PRESETS, seule source de verite — aucune valeur en dur
    ici), dans l'ordre D1 a D6."""
    rows = []
    ordered_levels = list(IntensityLevel)
    for preset_id in DurationPresetId:
        preset = DURATION_PRESETS[preset_id]
        free_max_index = ordered_levels.index(preset.free_max_level)
        free_levels = f"{ordered_levels[0].value} a {preset.free_max_level.value}"
        if free_max_index == len(ordered_levels) - 1:
            free_levels += " (tous)"
        rows.append(
            DurationPresetReferenceRow(
                id=preset_id.value.upper(),
                name=preset.name,
                total_minutes=preset.total_minutes,
                families=", ".join(
                    _FAMILY_LABELS[f] for f in TestFamily if f in preset.compatible_families
                ),
                free_levels=free_levels,
                reinforced_level=(
                    preset.reinforced_level.value if preset.reinforced_level is not None else "—"
                ),
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
        return _("Seul le débit (req/min) pilote ce test ; la simultanéité en découle.")
    if family is TestFamily.CONNECTION:
        return _("Seule la simultanéité (connexions) pilote ce test ; aucun débit cible.")
    return _(
        "Seul le débit au pic pilote ce test, atteint progressivement : sur une durée "
        "choisie plus courte que la rampe indiquée, le pic n'est jamais atteint."
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
# - _duration_label()/_precheck_label() (Phase 3, 2026-09-01) : 3 branches
#   distinctes (is_precheck_mandatory()/is_precheck_optional(), jamais un
#   seul booleen binaire) — un niveau gate optionnel (Puissant/Agressif)
#   n'est ni "jamais gate" ni "gate obligatoire" : le confondre avec l'un
#   des deux masquerait silencieusement soit la fourchette de durees,
#   soit l'extension via pre-check facultatif (bug reel corrige a
#   l'introduction du 3e palier, aucune exception levee avant le
#   correctif — juste un affichage errone). "(X min si pre-check)" ne
#   nomme jamais GATED_EXTENDED_DURATIONS_MINUTES en dur ici.
# - load_reference_family_note() : rappel qualitatif complementaire au
#   tableau chiffre, pour eviter la confusion notee par l'utilisateur
#   entre les deux dimensions d'un meme FixedRatePreset/RampPreset
#   (ex. Test requetes n'utilise jamais concurrent_connections, Test
#   charge n'utilise jamais peak_connections — voir engine_params.py).
# - duration_preset_reference_rows() (2026-09-01, mode "profil" D1-D6) :
#   AVANT ce correctif, les profils D1-D6 (deja fonctionnels dans les 3
#   ecrans de lancement et le CLI) n'apparaissaient nulle part dans
#   l'Aide — bug de decouvrabilite reel signale par l'utilisateur en
#   test. free_levels/reinforced_level derives de DurationPreset.
#   free_max_level/reinforced_level (ordre d'IntensityLevel, jamais de
#   plage en dur ici) — coherent avec le principe du fichier (rien
#   n'est invente, tout vient de domain/load/).
# Comment il sera utilise :
# - interfaces/tui/widgets/load_reference_table.py (DataTable),
#   interfaces/tui/widgets/duration_preset_table.py (DataTable D1-D6),
#   interfaces/tui/screens/help_screen.py (section "Reperes de charge").
# ---------------------------------------------------------------------->
