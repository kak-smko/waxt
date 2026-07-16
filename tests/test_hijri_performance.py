"""Performance tests for ``HijriCalendar`` using ``pytest-benchmark``
(requirement #12).

These do not assert tight timing thresholds (that would be flaky across
different machines/CI runners); instead they record reproducible
benchmarks via ``pytest-benchmark`` and apply only a very generous sanity
ceiling to catch catastrophic performance regressions (e.g. an
accidentally quadratic algorithm), without being sensitive to normal
hardware variance.

Run ``pytest tests/test_hijri_performance.py --benchmark-only
--benchmark-verbose`` to see detailed timing statistics.
"""

from __future__ import annotations

import datetime

import pytest

from tests.conftest import hijri_days_in_month
from waxt.calendar_converters import HijriCalendar

pytestmark = pytest.mark.performance

BATCH_SIZE = 2_000


def _gregorian_batch():
    start = datetime.date(1600, 1, 1)
    return [start + datetime.timedelta(days=i * 137) for i in range(BATCH_SIZE)]


def _hijri_batch():
    result = []
    for i in range(BATCH_SIZE):
        year = 1008 + (i % 900)
        month = 1 + (i % 12)
        day = 1 + (i % hijri_days_in_month(year, month))
        result.append((year, month, day))
    return result


def test_benchmark_gregorian_to_hijri(benchmark):
    batch = _gregorian_batch()

    def run():
        return [HijriCalendar.gregorian_to_hijri(d.year, d.month, d.day) for d in batch]

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 1.0  # generous ceiling: 1s for 2000 calls


def test_benchmark_hijri_to_gregorian(benchmark):
    batch = _hijri_batch()

    def run():
        return [HijriCalendar.hijri_to_gregorian(*d) for d in batch]

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 1.0


def test_benchmark_is_leap(benchmark):
    years = list(range(1, 1 + BATCH_SIZE))

    def run():
        return [HijriCalendar.is_leap(y) for y in years]

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 1.0


def test_benchmark_full_round_trip(benchmark):
    batch = _gregorian_batch()

    def run():
        results = []
        for d in batch:
            h = HijriCalendar.gregorian_to_hijri(d.year, d.month, d.day)
            results.append(HijriCalendar.hijri_to_gregorian(*h))
        return results

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 2.0
