# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Histogramme de latences fusionnable (Phase 1 du plan de charge distribuee, 2026-11-21).

Log-lineaire, bibliotheque standard seule : chaque puissance de 2 (en microsecondes) est coupee en
SUB_BUCKETS cases egales, soit une precision relative d'environ 1/SUB_BUCKETS (~1,6 %), de 1 µs a
plusieurs minutes. Chaque processus d'emission compte ses latences par seconde ; le parent FUSIONNE
les comptes (simple addition) et calcule p50/p95/p99 sur l'histogramme fusionne, jamais par moyenne
de percentiles (faux des que les processus ou les secondes n'ont pas le meme volume).

Representation : tuple trie de paires (indice de case, nombre), hashable et serialisable en JSON."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Mapping

SUB_BUCKETS = 64
_MIN_US = 1
Histogram = tuple[tuple[int, int], ...]


def bucket_of(latency_ms: float) -> int:
    micros = max(_MIN_US, int(latency_ms * 1000))
    exponent = micros.bit_length() - 1  # 2**exponent <= micros < 2**(exponent+1)
    if exponent < 6:  # en dessous de 64 µs : une case par microseconde
        return micros
    offset = (micros - (1 << exponent)) * SUB_BUCKETS >> exponent
    return 64 + (exponent - 6) * SUB_BUCKETS + offset


def bucket_value_ms(index: int) -> float:
    """Milieu de la case, en millisecondes."""
    if index < 64:
        return index / 1000
    exponent, offset = divmod(index - 64, SUB_BUCKETS)
    exponent += 6
    low = (1 << exponent) + (offset << exponent) / SUB_BUCKETS
    width = (1 << exponent) / SUB_BUCKETS
    return (low + width / 2) / 1000


def histogram_of(latencies_ms: Iterable[float]) -> Histogram:
    return freeze(Counter(bucket_of(value) for value in latencies_ms))


def freeze(counts: Mapping[int, int]) -> Histogram:
    return tuple(sorted((index, count) for index, count in counts.items() if count > 0))


def merge(histograms: Iterable[Histogram]) -> Histogram:
    total: Counter[int] = Counter()
    for histogram in histograms:
        for index, count in histogram:
            total[index] += count
    return freeze(total)


def count(histogram: Histogram) -> int:
    return sum(n for _, n in histogram)


def percentile_ms(histogram: Histogram, fraction: float) -> float:
    """Plus petite latence L telle qu'au moins `fraction` des requetes ont mis <= L. 0 si vide."""
    total = count(histogram)
    if total == 0:
        return 0.0
    rank = max(1, math.ceil(fraction * total - 1e-9))
    seen = 0
    for index, n in histogram:
        seen += n
        if seen >= rank:
            return bucket_value_ms(index)
    return bucket_value_ms(histogram[-1][0])
