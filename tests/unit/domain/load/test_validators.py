from omega_stress.core.enums import DurationPresetId, IntensityLevel, TestFamily
from omega_stress.core.results import Err, Ok
from omega_stress.domain.errors import (
    PrecheckRequiredError,
    UnauthorizedTargetError,
    ValidationError,
)
from omega_stress.domain.load import policies
from omega_stress.domain.load.builders import build_ramp_steps
from omega_stress.domain.load.duration_presets import (
    build_duration_preset_ramp_steps,
    duration_preset,
)
from omega_stress.domain.load.models import Duration, LoadPlan, Thresholds
from omega_stress.domain.load.validators import (
    evaluate_duration_preset,
    evaluate_generator_resources,
    evaluate_sliding_window,
    evaluate_threshold,
    validate_plan,
)
from omega_stress.domain.runs.models import ErrorBreakdown, IntervalSample, SystemSnapshot


def _plan(**overrides):
    defaults = dict(
        id="plan-1",
        family=TestFamily.REQUEST,
        level=IntensityLevel.BAS,
        duration=Duration(minutes=1),
        thresholds=Thresholds(max_error_rate=0.1),
        target_authorization_confirmed=True,
        precheck_validated=False,
        ramp_steps=(),
    )
    defaults.update(overrides)
    return LoadPlan(**defaults)


def test_valid_plan_passes():
    result = validate_plan(_plan())

    assert isinstance(result, Ok)


def test_unconfirmed_authorization_is_rejected():
    result = validate_plan(_plan(target_authorization_confirmed=False))

    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedTargetError)


def test_violent_without_precheck_is_rejected():
    result = validate_plan(
        _plan(
            level=IntensityLevel.VIOLENT, duration=Duration(minutes=1), precheck_validated=False
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, PrecheckRequiredError)


def test_violent_with_precheck_passes_at_a_base_duration():
    result = validate_plan(
        _plan(
            level=IntensityLevel.VIOLENT, duration=Duration(minutes=2), precheck_validated=True
        )
    )

    assert isinstance(result, Ok)


def test_violent_precheck_never_unlocks_an_extended_duration():
    # Different du palier gate OPTIONNEL (Puissant/Agressif, voir plus bas) :
    # pour un niveau gate OBLIGATOIRE, le pre-check conditionne l'acces au
    # niveau lui-meme, il ne debloque jamais de duree supplementaire — 4
    # min n'est jamais un choix ferme pour Violent/Maximum, meme avec
    # pre-check valide.
    result = validate_plan(
        _plan(
            level=IntensityLevel.VIOLENT, duration=Duration(minutes=4), precheck_validated=True
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)


def test_puissant_never_requires_precheck_to_start():
    # Palier gate OPTIONNEL : le run demarre sans pre-check, contrairement
    # au palier gate obligatoire ci-dessus.
    result = validate_plan(
        _plan(level=IntensityLevel.PUISSANT, duration=Duration(minutes=1), precheck_validated=False)
    )

    assert isinstance(result, Ok)


def test_puissant_extended_duration_requires_precheck():
    without_precheck = validate_plan(
        _plan(level=IntensityLevel.PUISSANT, duration=Duration(minutes=4), precheck_validated=False)
    )
    with_precheck = validate_plan(
        _plan(level=IntensityLevel.PUISSANT, duration=Duration(minutes=4), precheck_validated=True)
    )

    assert isinstance(without_precheck, Err)
    assert isinstance(without_precheck.error, ValidationError)
    assert isinstance(with_precheck, Ok)


def test_ramp_family_requires_ramp_steps():
    result = validate_plan(_plan(family=TestFamily.RAMP, ramp_steps=()))

    assert isinstance(result, Err)


def test_non_ramp_family_rejects_ramp_steps():
    steps = build_ramp_steps(IntensityLevel.BAS, duration_minutes=3)
    result = validate_plan(_plan(family=TestFamily.REQUEST, ramp_steps=steps))

    assert isinstance(result, Err)


def test_ramp_family_with_steps_passes():
    steps = build_ramp_steps(IntensityLevel.BAS, duration_minutes=3)
    result = validate_plan(_plan(family=TestFamily.RAMP, ramp_steps=steps))

    assert isinstance(result, Ok)


def test_evaluate_threshold_passes_within_bounds():
    thresholds = Thresholds(max_error_rate=0.1, max_p95_latency_ms=500)

    result = evaluate_threshold(
        observed_error_rate=0.05, observed_p95_latency_ms=300, thresholds=thresholds
    )

    assert isinstance(result, Ok)


def test_evaluate_threshold_flags_error_rate_breach():
    thresholds = Thresholds(max_error_rate=0.1)

    result = evaluate_threshold(
        observed_error_rate=0.2, observed_p95_latency_ms=None, thresholds=thresholds
    )

    assert isinstance(result, Err)


def test_evaluate_threshold_flags_latency_breach():
    thresholds = Thresholds(max_error_rate=0.5, max_p95_latency_ms=200)

    result = evaluate_threshold(
        observed_error_rate=0.0, observed_p95_latency_ms=250, thresholds=thresholds
    )

    assert isinstance(result, Err)


def _window_sample(at_second: float, *, request_count: int = 10, error_count: int = 0, errors=None):
    return IntervalSample(
        at_second=at_second,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=error_count,
        request_count=request_count,
        errors=errors if errors is not None else ErrorBreakdown(),
    )


def test_sliding_window_below_minimum_requests_is_ok_even_at_100pc_error_rate():
    samples = [_window_sample(1.0, request_count=5, error_count=5)]

    result = evaluate_sliding_window(samples, now_second=1.0)

    assert isinstance(result, Ok)


def test_sliding_window_flags_timeout_rate_breach():
    sample = _window_sample(5.0, request_count=40, errors=ErrorBreakdown(timeout=15))

    result = evaluate_sliding_window([sample], now_second=5.0)

    assert isinstance(result, Err)
    assert result.error.signal == "window_timeout_rate_exceeded"


def test_sliding_window_flags_http_5xx_rate_breach():
    sample = _window_sample(5.0, request_count=40, errors=ErrorBreakdown(http_5xx=8))

    result = evaluate_sliding_window([sample], now_second=5.0)

    assert isinstance(result, Err)
    assert result.error.signal == "window_http_5xx_rate_exceeded"


def test_sliding_window_flags_total_error_rate_breach():
    sample = _window_sample(5.0, request_count=40, error_count=15)

    result = evaluate_sliding_window([sample], now_second=5.0)

    assert isinstance(result, Err)
    assert result.error.signal == "window_error_rate_exceeded"


def test_sliding_window_critical_window_reacts_faster_than_main_window():
    # 26 s de trafic propre, puis un pic concentre dans les 3 dernieres
    # secondes : la fenetre 30s (denominateur large) ne depasse jamais
    # policies.WINDOW_TOTAL_ERROR_RATE_ABORT_THRESHOLD, mais la fenetre
    # critique 10s (denominateur plus petit, pic recent concentre) si —
    # preuve que la fenetre courte attrape ce que la fenetre longue seule
    # laisserait passer.
    samples = [_window_sample(float(sec)) for sec in range(1, 27)]
    samples += [_window_sample(float(sec), error_count=10) for sec in (27, 28, 29)]

    result = evaluate_sliding_window(samples, now_second=30.0)

    total_requests = sum(s.request_count for s in samples)
    total_errors = sum(s.error_count for s in samples)
    assert total_errors / total_requests < policies.WINDOW_TOTAL_ERROR_RATE_ABORT_THRESHOLD
    assert isinstance(result, Err)
    assert result.error.signal == "window_error_rate_exceeded"


def _resource_sample(at_second: float, system: SystemSnapshot | None) -> IntervalSample:
    return IntervalSample(
        at_second=at_second,
        observed_rate_per_minute=250.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        p99_latency_ms=30.0,
        error_count=0,
        request_count=10,
        system=system,
    )


def test_generator_resources_empty_history_is_ok():
    assert isinstance(evaluate_generator_resources([]), Ok)


def test_generator_resources_missing_latest_snapshot_is_ok():
    samples = [_resource_sample(1.0, None)]

    assert isinstance(evaluate_generator_resources(samples), Ok)


def test_generator_resources_high_cpu_without_enough_consecutive_samples_is_ok():
    samples = [
        _resource_sample(
            1.0, SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0)
        ),
        _resource_sample(
            2.0, SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0)
        ),
    ]

    assert isinstance(evaluate_generator_resources(samples), Ok)


def test_generator_resources_flags_sustained_high_cpu():
    samples = [
        _resource_sample(
            float(i), SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0)
        )
        for i in range(1, 4)
    ]

    result = evaluate_generator_resources(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "generator_cpu_exceeded"


def test_generator_resources_high_generator_cpu_alone_is_ok():
    # Bug reel corrige le 2026-09-01 (captures d'ecran) : un test
    # Connexions normal (Moyen/Haut) sature legitimement ~22-25% de CPU
    # generateur sur une machine 4 coeurs SAINE (RAM/autres coeurs
    # intacts) — le CPU generateur seul ne doit plus jamais arreter un
    # test, meme tres eleve, si le reste de la machine reste disponible.
    samples = [
        _resource_sample(
            float(i), SystemSnapshot(cpu_percent_generator=99.0, cpu_percent_global=30.0)
        )
        for i in range(1, 4)
    ]

    assert isinstance(evaluate_generator_resources(samples), Ok)


def test_generator_resources_high_global_cpu_alone_is_ok():
    # Symetrique : un CPU machine eleve pour une raison EXTERIEURE au
    # generateur (autre logiciel) ne doit pas etre impute au generateur
    # ni declencher ce garde-fou specifique.
    samples = [
        _resource_sample(
            float(i), SystemSnapshot(cpu_percent_generator=5.0, cpu_percent_global=95.0)
        )
        for i in range(1, 4)
    ]

    assert isinstance(evaluate_generator_resources(samples), Ok)


def test_generator_resources_missing_global_cpu_never_aborts():
    samples = [
        _resource_sample(
            float(i), SystemSnapshot(cpu_percent_generator=99.0, cpu_percent_global=None)
        )
        for i in range(1, 4)
    ]

    assert isinstance(evaluate_generator_resources(samples), Ok)


def test_generator_resources_cpu_threshold_scales_with_core_count():
    # Non-regression (bug reel, 2026-09-01) : le seuil d'arret est
    # relatif a ce qu'UN SEUL coeur peut fournir sur la machine, jamais
    # un pourcentage absolu fixe — sur 8 coeurs, le plafond normalise
    # pour un moteur mono-coeur est 100/8=12.5%, le seuil d'arret est
    # donc ~11.9% (0.95 * 12.5), tres different du seuil sur 1 coeur (95%).
    # cpu_percent_global sature volontairement (95%) sur les deux cas :
    # seul le seuil CPU generateur est ici sous test.
    below_threshold = [
        _resource_sample(
            float(i),
            SystemSnapshot(
                cpu_percent_generator=11.0, cpu_percent_global=95.0, logical_cpu_count=8
            ),
        )
        for i in range(1, 4)
    ]
    above_threshold = [
        _resource_sample(
            float(i),
            SystemSnapshot(
                cpu_percent_generator=12.0, cpu_percent_global=95.0, logical_cpu_count=8
            ),
        )
        for i in range(1, 4)
    ]

    assert isinstance(evaluate_generator_resources(below_threshold), Ok)
    result = evaluate_generator_resources(above_threshold)
    assert isinstance(result, Err)
    assert result.error.signal == "generator_cpu_exceeded"


def test_generator_resources_full_single_core_saturation_still_triggers_on_multicore():
    # Un moteur asyncio (lie au GIL) qui sature reellement son seul coeur
    # utilisable doit encore declencher l'arret, meme sur une machine a
    # plusieurs coeurs, MAIS seulement si la machine entiere (cpu_percent_
    # global) est aussi sous pression (2026-09-01, second correctif) —
    # ~25% normalise sur 4 coeurs (proche du plafond atteignable), au-
    # dessus du seuil ~23.75% (0.95 * 100/4).
    samples = [
        _resource_sample(
            float(i),
            SystemSnapshot(
                cpu_percent_generator=25.0, cpu_percent_global=95.0, logical_cpu_count=4
            ),
        )
        for i in range(1, 4)
    ]

    result = evaluate_generator_resources(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "generator_cpu_exceeded"


def test_generator_resources_missing_core_count_defaults_to_conservative_single_core():
    # logical_cpu_count absent (mesure ratee) retombe sur l'hypothese la
    # plus conservatrice (1 coeur, seuil ~95%) plutot que de desactiver
    # silencieusement le garde-fou.
    samples = [
        _resource_sample(
            float(i), SystemSnapshot(cpu_percent_generator=99.0, cpu_percent_global=95.0)
        )
        for i in range(1, 4)
    ]

    result = evaluate_generator_resources(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "generator_cpu_exceeded"


def test_generator_resources_ignores_isolated_cpu_dip_within_window():
    # cpu_percent_global sature (95%) sur les 4 echantillons : c'est bien
    # la logique de fenetre glissante du CPU generateur qui est testee
    # ici, pas la condition globale (2026-09-01, second correctif).
    samples = [
        _resource_sample(1.0, SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0)),
        _resource_sample(2.0, SystemSnapshot(cpu_percent_generator=10.0, cpu_percent_global=95.0)),
        _resource_sample(3.0, SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0)),
        _resource_sample(4.0, SystemSnapshot(cpu_percent_generator=95.0, cpu_percent_global=95.0)),
    ]

    assert isinstance(evaluate_generator_resources(samples), Ok)


def test_generator_resources_flags_low_available_memory():
    samples = [_resource_sample(1.0, SystemSnapshot(memory_available_percent=10.0))]

    result = evaluate_generator_resources(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "generator_memory_exceeded"


def test_generator_resources_flags_open_files_ratio_breach():
    samples = [
        _resource_sample(1.0, SystemSnapshot(open_files=800, open_files_soft_limit=1000))
    ]

    result = evaluate_generator_resources(samples)

    assert isinstance(result, Err)
    assert result.error.signal == "generator_fds_exceeded"


def test_generator_resources_missing_soft_limit_never_raises_or_flags():
    samples = [_resource_sample(1.0, SystemSnapshot(open_files=800, open_files_soft_limit=None))]

    assert isinstance(evaluate_generator_resources(samples), Ok)


# --- evaluate_duration_preset() (mode "profil" D1-D6) ---

_D4 = duration_preset(DurationPresetId.D4)  # free_max=AGRESSIF, reinforced=VIOLENT


def test_duration_preset_level_within_free_range_passes():
    result = evaluate_duration_preset(
        IntensityLevel.PUISSANT, _D4, reinforced_confirmation_text=None
    )

    assert isinstance(result, Ok)


def test_duration_preset_reinforced_level_without_text_is_rejected():
    result = evaluate_duration_preset(
        IntensityLevel.VIOLENT, _D4, reinforced_confirmation_text=None
    )

    assert isinstance(result, Err)


def test_duration_preset_reinforced_level_with_wrong_text_is_rejected():
    result = evaluate_duration_preset(
        IntensityLevel.VIOLENT, _D4, reinforced_confirmation_text="pas le bon texte"
    )

    assert isinstance(result, Err)


def test_duration_preset_reinforced_level_with_exact_text_passes():
    result = evaluate_duration_preset(
        IntensityLevel.VIOLENT,
        _D4,
        reinforced_confirmation_text=policies.REINFORCED_CONFIRMATION_PHRASE,
    )

    assert isinstance(result, Ok)


def test_duration_preset_level_beyond_reinforced_is_rejected_even_with_text():
    result = evaluate_duration_preset(
        IntensityLevel.MAXIMUM,
        _D4,
        reinforced_confirmation_text=policies.REINFORCED_CONFIRMATION_PHRASE,
    )

    assert isinstance(result, Err)


# --- validate_plan() en mode "profil" (duration_preset_id renseigne) ---


def test_validate_plan_rejects_incompatible_family_for_preset():
    d6 = duration_preset(DurationPresetId.D6)
    result = validate_plan(
        _plan(
            family=TestFamily.REQUEST,
            level=IntensityLevel.BAS,
            duration=Duration(minutes=d6.total_minutes),
            duration_preset_id=DurationPresetId.D6,
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)


def test_validate_plan_rejects_duration_mismatch_with_preset():
    result = validate_plan(
        _plan(
            level=IntensityLevel.BAS,
            duration=Duration(minutes=1),
            duration_preset_id=DurationPresetId.D4,
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)


def test_validate_plan_accepts_matching_preset_and_free_level():
    result = validate_plan(
        _plan(
            level=IntensityLevel.PUISSANT,
            duration=Duration(minutes=_D4.total_minutes),
            duration_preset_id=DurationPresetId.D4,
        )
    )

    assert isinstance(result, Ok)


def test_validate_plan_connection_family_may_carry_ramp_steps_with_preset():
    # Relaxe la regle habituelle ("seul Test charge porte des ramp_steps")
    # UNIQUEMENT quand duration_preset_id est renseigne.
    d1 = duration_preset(DurationPresetId.D1)
    result = validate_plan(
        _plan(
            family=TestFamily.CONNECTION,
            level=IntensityLevel.BAS,
            duration=Duration(minutes=d1.total_minutes),
            duration_preset_id=DurationPresetId.D1,
            ramp_steps=build_duration_preset_ramp_steps(d1),
        )
    )

    assert isinstance(result, Ok)


def test_validate_plan_connection_family_still_rejects_ramp_steps_in_manual_mode():
    d1 = duration_preset(DurationPresetId.D1)
    result = validate_plan(
        _plan(
            family=TestFamily.CONNECTION,
            level=IntensityLevel.BAS,
            ramp_steps=build_duration_preset_ramp_steps(d1),
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)
