"""Performance tests using ``pytest-benchmark`` (requirement #11).

These do not assert tight timing thresholds (that would be flaky across
different machines/CI runners); instead they record reproducible
benchmarks via ``pytest-benchmark`` and apply only a very generous sanity
ceiling to catch catastrophic performance regressions (e.g. an
accidentally quadratic algorithm), without being sensitive to normal
hardware variance.

Run ``pytest tests/test_jalali_performance.py --benchmark-only
--benchmark-verbose`` to see detailed timing statistics.
"""

from __future__ import annotations

import datetime

import pytest

from waxt.calendar_converters import JalaliCalendar

pytestmark = pytest.mark.performance

BATCH_SIZE = 2_000


def _gregorian_batch():
    start = datetime.date(1600, 1, 1)
    return [start + datetime.timedelta(days=i * 137) for i in range(BATCH_SIZE)]


def _jalali_batch():
    return [(979 + (i % 900), 1 + (i % 12), 1 + (i % 25)) for i in range(BATCH_SIZE)]


def test_benchmark_gregorian_to_jalali(benchmark):
    batch = _gregorian_batch()

    def run():
        return [
            JalaliCalendar.gregorian_to_jalali(d.year, d.month, d.day) for d in batch
        ]

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 1.0  # generous ceiling: 1s for 2000 calls


def test_benchmark_jalali_to_gregorian(benchmark):
    batch = _jalali_batch()

    def run():
        return [JalaliCalendar.jalali_to_gregorian(*d) for d in batch]

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 1.0


def test_benchmark_is_leap(benchmark):
    years = list(range(979, 979 + BATCH_SIZE))

    def run():
        return [JalaliCalendar.is_leap(y) for y in years]

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 1.0


def test_benchmark_full_round_trip(benchmark):
    batch = _gregorian_batch()

    def run():
        results = []
        for d in batch:
            j = JalaliCalendar.gregorian_to_jalali(d.year, d.month, d.day)
            results.append(JalaliCalendar.jalali_to_gregorian(*j))
        return results

    result = benchmark(run)
    assert len(result) == BATCH_SIZE
    assert benchmark.stats.stats.mean < 2.0
