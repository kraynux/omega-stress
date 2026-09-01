from omega_stress.domain.errors import ThresholdExceededError


def test_threshold_exceeded_error_defaults_to_the_historical_signal():
    # Non-regression (Phase 2 garde-fous) : tout appelant existant qui
    # construit un ThresholdExceededError sans signal= explicite (ex.
    # evaluate_threshold(), inchange depuis avant Phase 2) doit garder
    # exactement le meme comportement qu'avant l'ajout de cet attribut.
    error = ThresholdExceededError("Taux d'erreur observe 20.0% > seuil 10.0%")

    assert error.signal == "threshold_exceeded"


def test_threshold_exceeded_error_accepts_an_explicit_signal():
    error = ThresholdExceededError("CPU generateur >= 90%", signal="generator_cpu_exceeded")

    assert error.signal == "generator_cpu_exceeded"
