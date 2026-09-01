import resource

import pytest

from omega_stress.infrastructure.probe.live_probe import LiveSystemSampler


def test_sample_returns_a_populated_snapshot():
    sampler = LiveSystemSampler()

    snapshot = sampler.sample()

    # cpu_percent_generator peut valoir 0.0 au tout premier appel utile
    # (delta depuis l'amorçage en __init__, voir live_probe.py) — jamais
    # None sur un poste ou psutil fonctionne normalement.
    assert snapshot.cpu_percent_generator is not None
    assert snapshot.cpu_percent_global is not None
    assert snapshot.memory_available_percent is not None
    assert snapshot.memory_rss_mb is not None
    assert snapshot.memory_rss_mb > 0
    assert snapshot.swap_used_mb is not None


def test_repeated_samples_never_raise():
    """sample() est appelee une fois par intervalle pendant un run
    (potentiellement des centaines de fois) — jamais d'exception,
    meme sur des appels rapproches."""
    sampler = LiveSystemSampler()

    for _ in range(5):
        snapshot = sampler.sample()
        assert snapshot.cpu_percent_generator is not None


def test_open_files_soft_limit_matches_resource_getrlimit():
    sampler = LiveSystemSampler()
    expected_soft_limit, _ = resource.getrlimit(resource.RLIMIT_NOFILE)

    snapshot = sampler.sample()

    assert snapshot.open_files_soft_limit == expected_soft_limit


def test_open_files_soft_limit_is_stable_across_samples():
    """Lue une seule fois en __init__ (voir live_probe.py) : ne doit
    jamais varier d'un sample() a l'autre pendant le meme run."""
    sampler = LiveSystemSampler()

    first = sampler.sample().open_files_soft_limit
    second = sampler.sample().open_files_soft_limit

    assert first == second


def test_cpu_percent_generator_is_normalized_by_logical_cpu_count():
    """Non-regression (bug reel, 2026-09-01) : psutil.Process.cpu_percent()
    n'est pas normalise par le nombre de coeurs — un run "Maximum"
    s'arretait au bout de 3s (diagnostic ">90%") alors que l'utilisation
    globale machine restait tres basse, un seul coeur sature suffisant a
    atteindre ~100% en mesure brute. cpu_percent_generator doit rester sur
    la meme echelle 0-100 que cpu_percent_global."""
    sampler = LiveSystemSampler()
    sampler._process.cpu_percent = lambda interval=None: 100.0  # type: ignore[method-assign]

    snapshot = sampler.sample()

    assert snapshot.cpu_percent_generator == pytest.approx(100.0 / sampler._logical_cpu_count)


def test_logical_cpu_count_is_a_positive_stable_value():
    # Pas de comparaison stricte a os.cpu_count() : peut diverger de
    # psutil.cpu_count() dans un environnement a affinite CPU restreinte
    # (conteneur/cgroup) — seule la positivite et la stabilite comptent
    # ici (voir live_probe.py, lu une seule fois en __init__).
    sampler = LiveSystemSampler()

    first = sampler.sample().logical_cpu_count
    second = sampler.sample().logical_cpu_count

    assert first is not None and first > 0
    assert first == second
